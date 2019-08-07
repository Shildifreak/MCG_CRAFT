import sys, os
if __name__ == "__main__":
	sys.path.append(os.path.abspath("../.."))
	__package__ = "voxelengine.server"

from collections import defaultdict

from voxelengine.server.blocks.block_world import BlockWorld
from voxelengine.server.event_system import EventSystem
from voxelengine.server.entities.entity_world import EntityWorld
from voxelengine.server.players.player_world import PlayerWorld

class Clock(dict):
	def __init__(self, *args, **kwargs):
		super(Clock, self).__init__(*args, **kwargs)
	current_gametick = property(lambda self:self["gametick"], lambda self, value:self.__setitem__("gametick",value))
	def tick(self):
		self.current_gametick += 1

class World(object):
	def __init__(self, data):
		metadata = data["metadata"]
		self.clock = Clock(metadata["clock"])
		self.event_system = EventSystem(self, data["events"])
		self.entities = EntityWorld()
		self.blocks = BlockWorld(data["block_world"], self.event_system, self.clock)
		self.players = PlayerWorld(data["players"])
	
	def __getitem__(self, *args, **kwargs):
		#M# raise DeprecationWarning("use world.blocks[...] instead of world[...]")
		return self.blocks.__getitem__(*args,**kwargs)
	
	def __setitem__(self, *args, **kwargs):
		#M# raise DeprecationWarning("use world.blocks[...] instead of world[...]")
		self.blocks.__setitem__(*args,**kwargs)

	def tick(self):
		# process pending events
		self.event_system.process_events()
		# tick
		self.event_system.tick()
		self.clock.tick()






if __name__ == "__main__":
	from voxelengine.server.world import World
	from voxelengine.server.world_data_example import data    
	data["block_world"]["generator"] = {
		"name":"Simple Terrain Generator",
		"seed":0,
		"path":"...",
		"code":\
"""
def terrain(position):
	\"""a very simple terrain generator -> flat map with checkerboard pattern\"""
	if position[1] == -2:
		return "GREEN" if (position[0]+position[2]) % 2 else "CYAN"
	return "AIR"
def init(welt):
	pass
spawnpoint = (0,0,0)
"""
	}

	w = World(data)

	print(w.blocks[(0,-2,0)])
	w.blocks[(0,-2,0)] = "AIR"
	w.clock.current_gametick += 1
	print(w.blocks[(0,-2,0)])
	print("THIS SECOND ONE SHOULD BE AIR IF AT LEAST ONE GAMETICK HAS PASSED")

	from voxelengine.server.entities.entity import Entity
	e = Entity()










###############################################################################################################################################################################
###############################################################################################################################################################################
###############################################################################################################################################################################

if False:
	import zipfile

	class World(object):
		BlockClass = Block
		PlayerEntityClass = Entity
		def __init__(self, worldgenerators = [], filename = None, spawnpoint=(0,0,0), chunksize = 4, defaultblock = "AIR"):
			"""create new World instance"""
			self.entities = set()
			self.players = set()
			if filename != None:
				self._load(filename)

		def _load(self,filename):
			if os.path.exists(filename):
				with zipfile.ZipFile(filename,"r",allowZip64=True) as zf:
					metadata = ast.literal_eval(zf.read("metadata.py"))
					if metadata["chunksize"] != self.chunksize:
						raise RuntimeError("It is currently not possible to load Worlds that were saved with another chunksize.")
					if metadata["version"] < self.FILEFORMATVERSION:
						raise RuntimeError("This world was saved in an older version of the game. Please contact the developer for a way to convert it.")
					if metadata["version"] > self.FILEFORMATVERSION:
						raise RuntimeError("This world was saved in a newer version of the game. Please update your game in order to be able to play it.")
					for name in zf.namelist():
						if name.startswith("c") and name.endswith(".py"):
							basename = name.rsplit(".",1)[0]
							_,x,y,z = basename.split("_")
							chunkmeta = ast.literal_eval(zf.read(name))
							compressed_data = zf.read(basename+".bin")
							initlevel = chunkmeta[0]
							block_codec = map(BlockData, chunkmeta[1])
							position = Vector(map(int,(x,y,z)))

							c = ServerChunk(self.chunksize,self,position)
							c.initlevel = initlevel
							c.compressed_data = compressed_data
							c.block_codec = block_codec
							self.chunks[position] = c
			else:
				if "-debug" in sys.argv:
					print("File %s not found." %filename)

		FILEFORMATVERSION = 1

		def save(self,filename):
			"""save the world into a file"""
			with zipfile.ZipFile(filename,"w",allowZip64=True) as zf:
				metadata = {"chunksize": self.chunksize,
							"version"  : self.FILEFORMATVERSION,
							"timestamp": time.time(),
							}
				zf.writestr("metadata.py",repr(metadata))
				for position,chunk in self.chunks.items():
					x,y,z = map(str,chunk.position)
					name = "_".join(("c",x,y,z))
					chunkmeta = (chunk.initlevel, chunk.block_codec)
					zf.writestr(name+".py", repr(chunkmeta))
					zf.writestr(name+".bin", chunk.compressed_data)
