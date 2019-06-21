from blocks.block_world import BlockWorld

class World(object):
	def __init__(self, savefile):
		
		data = WORLD_DATA #M#
		metadata = data["metadata"]
		self.clock = Clock(metadata["timestamp"])
		self.event_system = EventSystem()
		self.entities = EntityWorld()
		self.blocks = BlockWorld(data["block_world"], self.event_system, self.clock)
		self.metadata = None
		self.seed = None
		pass
	
	def __getitem__(self, *args, **kwargs):
		#M# raise DeprecationWarning("use world.blocks[...] instead of world[...]")
		return self.blocks.__getitem__(*args,**kwargs)
	
	def __setitem__(self, *args, **kwargs):
		#M# raise DeprecationWarning("use world.blocks[...] instead of world[...]")
		self.blocks.__setitem__(*args,**kwargs)
	
	def save(self):
		pass
	def tick(self):
		pass

###############################################################################################################################################################################
###############################################################################################################################################################################
###############################################################################################################################################################################

if False:

	#* encoding: utf-8 *#

	import math
	import time
	import threading #used by client and has to be imported before thread, cause otherwise some internal monkey patching causes error on termination
	import thread
	import ast
	import itertools
	import zipfile

	import sys,os,inspect
	# Adding directory modules to path
	PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
	sys.path.append(os.path.join(PATH,"modules"))

	from shared import *
	from observableCollections import *
	from message_buffer import MessageBuffer
	#import textures

	DOASYNCLOAD = True
	MAX_LOAD_THREADS = 1

	# merke: wenn man from voxelengine import * macht werden neue globale Variablen nach dem import nicht übernommen :(
	# ergo: globale Variablen nicht mehr ändern zur Laufzeit (verändern der Objekte ist ok)
		
	class World(object):
		BlockClass = Block
		PlayerEntityClass = Entity
		def __init__(self, worldgenerators = [], filename = None, spawnpoint=(0,0,0), chunksize = 4, defaultblock = "AIR"):
			"""create new World instance"""
			self.worldgenerators = worldgenerators
			self.spawnpoint = Vector(spawnpoint)
			if not isinstance(defaultblock,Block):
				defaultblock = self.BlockClass(defaultblock)
			self.defaultblock = defaultblock
			self.loading_queue = []
			self.load_thread_count = 0
			self.chunks = {}
			self.entities = set()
			self.players = set()
			if filename != None:
				self._load(filename)
			assert issubclass(self.BlockClass, Block)
	   
		def spawn_player(self,player):
			spielfigur = self.PlayerEntityClass()
			spielfigur.set_world(self,self.spawnpoint)
			player.observe(spielfigur)

		DATA = {
			"metadata":{
				"timestep":0,
				"generator":"colorland",
			},
			"blocks":{
			},
			"entities":{
			},
			"events":{
			}
		}

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
