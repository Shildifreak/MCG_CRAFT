from blocks.blockdata_encoder import BlockDataEncoder
from blocks.block_world import BlockWorld
from blocks.block_world_index import BlockWorldIndex

class World(object):
	def __init__(self, savefile, generator):
		
		data = DATA #M#
		metadata = data["metadata"]
		self.entity_world = EntityWorld()
		self.block_world = BlockWorld(data["blocks"], metadata["timestamp"])
		self.block_world_index = BlockIndex(self.get_tags)
		self.event_system = EventSystem()
		self.metadata = None
		self.terrain_generator = None
		self.seed = None
		pass

	def get_block(self, position):
		# get_block_id
		# translate_from_block_id
		# if no block there use terrain_generator
		if timestep == 0:
			return self.terrain_generator[position]
		pass
	def set_block(self, position, value):
		# translate to block_id
		# check with terrain_generator to see if to delete
		# delete or set
		# update BlockWorldIndex
		pass
	def get_tags(self, position):
		pass
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
        
    class Block(dict):
        def __new__(cls,data):
            if isinstance(data,basestring):
                data = {"id":data}
            else:
                assert "id" in data
            data = BlockData(data)
        def __init__(self, position, world):
            self.position = position
            self.world = world
        """
        def __getitem__(self,key):
            return self.data[key]
        def __setitem__(self,key,value=delvalue):
            if self.data.immutable() and (self.chunk != None): # <=> data may be used by multiple Blocks
                self.data = BlockData(self.data.copy())
                self.data[key] = value
                self.chunk.set_block(self.position, self)
            else:
                self.data[key] = value
        def __delitem__(self,key): # make that stuff prettier
            if self.data.immutable() and (self.chunk != None):
                self.data = BlockData(self.data.copy())
                del self.data[key]
                self.chunk.set_block(self.position, self)
            else:
                del self.data[key]
        """
        def __eq__(self,other):
            if isinstance(other,dict):
                return dict.__eq(self,other)
            elif isinstance(other,basestring):
                return self["id"] == other
            else:
                return False
        def __ne__(self,other):
            return not (self == other)
        
        def client_version(self):
            orientation = self.get("base","")+str(self.get("rotation",""))
            blockmodel = self["id"]+self.get("state","")
            if orientation:
                return blockmodel+":"+orientation
            else:
                return blockmodel

        def tags(self):
            return set()
        
        def save(self):
            """make changes that were applied to this Block persistent in the world"""
            self.world[self.position] = self

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

        def __getitem__(self, position):
            return self.get_block(position)

        def __setitem__(self, position, block):
            self.set_block(position, block)

        def get_block(self, position, minlevel = None, load_on_miss = True):
            """get block at position

            args (Argumente):
                position    : (x,y,z)
            kwargs (optionale Argumente):
                minlevel    : required initlevel of chunk (defaults to max)
                load_on_miss: whether to load chunk if necessary
                              if False requests for unloaded chunks return None
            """
            position = Vector(position)
            chunk = self._get_chunk(position, minlevel, load_on_miss)
            if chunk == None:
                return None
            return chunk.get_block(position)

        def set_block(self, position, block, minlevel = None, load_on_miss = True):
            """set block at position"""
            position = Vector(position)
            chunk = self._get_chunk(position, minlevel, load_on_miss)
            if chunk == None:
                return False
            chunk.set_block(position,block)
            return True
        
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
