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
#import textures

DOASYNCLOAD = True
MAX_LOAD_THREADS = 1

# merke: wenn man from voxelengine import * macht werden neue globale Variablen nach dem import nicht übernommen :(
# ergo: globale Variablen nicht mehr ändern zur Laufzeit (verändern der Objekte ist ok)

class BlockData(dict):
    def __eq__(self,other):
        if isinstance(other,BlockData):
            if self.immutable() and other.immutable():
                return dict.__eq__(self, other)
        return False
    def __ne__(self,other):
        return not (self == other)
    def immutable(self):
        for v in self.values():
            try:
                hash(v)
            except TypeError:
                return False
        return True
    def client_version(self):
        orientation = self.get("base","")+str(self.get("rotation",""))
        blockmodel = self["id"]+self.get("state","")
        if orientation:
            return blockmodel+":"+orientation
        else:
            return blockmodel
    
class Block(object):
    delvalue = object()
    def __init__(self,data):
        if isinstance(data,basestring):
            data = {"id":data}
        else:
            assert "id" in data
        self.data = BlockData(data)
        self.chunk = None
        self.position = None
        self.world = None
    def __getitem__(self,key):
        return self.data[key]
    #def get(self,key,*default):
    #    return self.data.get(key,*default)
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
    def __eq__(self,other):
        if isinstance(other,Block):
            return self.data == other.data
        elif isinstance(other,dict):
            return self.data == other
        elif isinstance(other,basestring):
            return self["id"] == other
        else:
            return False
    def __ne__(self,other):
        return not (self == other)
    
    def __repr__(self):
        return "Block(%s)" % repr(self.data)

class ServerChunk(Chunk):
    """The (Server)Chunk class is only relevant when writing a world generator
    
    you can iterate over the positions in a chunk by:
    >>> for position in chunk:
    >>>     ...
    """
    def __init__(self, chunksize, world, position):
        Chunk.__init__(self,chunksize,[world.defaultblock.data])
        self.world = world
        self.position = position # used for sending chunk to player
        self.observers = set() #if empty and chunk not altered, it should be removed
        self.lock = thread.allocate_lock()
        self._initlevel = -1

    @property
    def initlevel(self):
        return self._initlevel
    
    @initlevel.setter
    def initlevel(self,value):
        self._initlevel = value
        if self.is_fully_generated():
            for player in self.world.players:
                player._notice_new_chunk(self)


    def __iter__(self):
        """iterate over positions in chunk"""
        p = self.position<<self.chunksize
        c = 1<<self.chunksize
        for dx in xrange(c):
            for dy in xrange(c):
                for dz in xrange(c):
                    yield p+(dx,dy,dz)

    def get_block(self, position):
        """
        like normal Chunks get_block but
        - searches world if position is not within chunk (with own initlevel-1)
        - recommended for getting blocks of other chunks in terrain generators
        """
        if not isinstance(position,Vector):
            position = Vector(position)
        if (position>>self.chunksize) == self.position:
            block_data = Chunk.get_block(self,position)
            block = self.world.BlockClass(block_data)
            block.world, block.chunk, block.position = self.world, self, position
            return block
        else:
            return self.world.get_block(position,self.initlevel-1)
    
    def set_block(self, position, block):
        """
        like normal Chunks set_block but
        - searches world if position is not within chunk (with own initlevel-1)
        - recommended for setting blocks of other chunks in terrain generators
        """
        if isinstance(block,self.world.BlockClass):
            block_data = block.data
        else:
            block_data = self.world.BlockClass(block).data
        if not isinstance(position,Vector):
            position = Vector(position)
        if (position>>self.chunksize) == self.position:
            for observer in self.observers:
                observer._notice_block(position,block_data)
            block_data = Chunk.set_block(self,position,block_data)
            if isinstance(block, self.world.BlockClass):
                block.data = block_data
                block.world, block.chunk, block.position = self.world, self, position
        else:
            self.world.set_block(position,block_data,self.initlevel-1)

    def get_entities(self):
        return (entity for entity in self.world.entities if (entity["position"].normalize()>>self.chunksize) == self.position)
    
    def is_fully_generated(self):
        return self.initlevel == len(self.world.worldgenerators)

class Entity(ObservableDict):
    def __init__(self,data = None):
        ObservableDict.__init__(self,data if data != None else {})
        self.world = None
        self.observers = set()
        self.old_chunk_observers = set()

        self.setdefault("position",(0,0,0))
        self.setdefault("rotation",(0,0))
        self.setdefault("texture",0)
        self.setdefault("speed",5)

        self.register_item_callback(self._on_position_change,"position")
        self.register_item_callback(self._notify_chunk_observers,"rotation")
        self.register_item_callback(self._notify_chunk_observers,"texture")
        self.register_item_sanitizer(lambda pos: Vector(pos),"position")

    def _on_position_change(self, new_position):
        """set position of entity"""
        # stuff so other players can see me move
        new_chunk_observers = self.world._get_chunk(new_position).observers if self.world and new_position else set()
        for o in self.old_chunk_observers.difference(new_chunk_observers):         # tell everyone who doesn't also observe the new position that I'm gone
            o._del_entity(self)
        for o in new_chunk_observers:        # tell everyone who is observing the new position that I'm now here
            o._set_entity(self)
        self.old_chunk_observers = new_chunk_observers
        
        # stuff so own players move
        for observer in self.observers:
            observer._notice_position()

    def set_world(self, new_world, new_position):
        """ adjust to new world """
        # savely remove from old world
        old_world = self.world
        if old_world:
            self.world.entities.discard(self)
        # add to new world:
        self.world = new_world
        if new_world:
            new_world.entities.add(self)
        self["position"] = new_position
        for observer in self.observers:
            observer._notice_world(old_world,new_world)
        
    def get_sight_vector(self):
        """ Returns the current line of sight vector indicating the direction
        the entity is looking.

        """
        x, y = self["rotation"]
        # y ranges from -90 to 90, or -pi/2 to pi/2, so m ranges from 0 to 1 and
        # is 1 when looking ahead parallel to the ground and 0 when looking
        # straight up or down.
        m = math.cos(math.radians(y))
        # dy ranges from -1 to 1 and is -1 when looking straight down and 1 when
        # looking straight up.
        dy = math.sin(math.radians(y))
        dx = math.cos(math.radians(x - 90)) * m
        dz = math.sin(math.radians(x - 90)) * m
        return Vector((dx, dy, dz))

    def _notify_chunk_observers(self,*_):
        if self.world:
            for observer in self.world._get_chunk(self["position"]).observers:
                observer._set_entity(self)

class GotoGroup(object):
    def __init__(self):
        self.message = None
    def add(self, message):
        self.message = message
    def pop(self):
        m, self.message = self.message, None
        return m
class FifoGroup(collections.deque):
    add = collections.deque.append
    def pop(self):
        if self:
            return self.popleft()
        #return None
#class TellFifoGroup(FifoGroup):
#    def pop(self):
#        print len(self)
#        return FifoGroup.pop(self)
class EntityGroup(object):
    def __init__(self):
        self.content = collections.OrderedDict()
    def add(self,message):
        self.content[message[1]] = message
    def pop(self):
        if self.content:
            return self.content.popitem(last=False)[1]
        #return None

class BlockGroup(object):
    def __init__(self):
        self.serialized = []
        self.unserialized = collections.OrderedDict()
        self.chunksize = None
    def add(self,message):
        if message[0] == "chunksize":
            self.chunksize = message[1]
        # only optimize when chunksize is known
        if self.chunksize:
            # area
            if message[0] in ("setarea","delarea"):
                chunkposition = message[1]
                self.unserialized = collections.OrderedDict((k,v) for k,v in self.unserialized.iteritems() if not self.in_chunk(message,chunkposition))
                self.unserialized[("chunk",chunkposition)] = message
                return
            # block
            if message[0] in ("set","del"):
                blockposition = message[1]
                self.unserialized[("block",blockposition)] = message
                return
        # default: serialize everything
        self.serialized.extend(self.unserialized.values())
        self.unserialized.clear()
        self.serialized.append(message)
    def pop(self):
        if self.serialized:
            return self.serialized.pop(0)
        if self.unserialized:
            return self.unserialized.popitem(last=False)[1]
        # return None
    @staticmethod
    def in_chunk(message, chunkposition):
        if message[0] in ("set","del"):
            blockposition = message[1]
            return (blockposition >> self.chunksize) == chunkposition
        else:
            return False
            
class MessageBuffer(object):
    def __init__(self):
        goto_group = GotoGroup()
        entity_group = EntityGroup()
        vip_entity_group = EntityGroup()
        block_group = BlockGroup()
        misc_group = FifoGroup()
        hud_group = FifoGroup()
        self.group_of = {"goto":(goto_group,),
                         "setentity":(entity_group,vip_entity_group), "delentity":(entity_group,vip_entity_group),
                         "set":(block_group,), "del":(block_group,), "setarea":(block_group,), "delarea":(block_group,), "clear":(block_group,), "chunksize":(block_group,),
                         "focusdist":(misc_group,), "setup":(misc_group,),
                         "sethud":(hud_group,), "delhud":(hud_group,), "focushud":(hud_group,),
                        }
        self.groups = (misc_group, vip_entity_group, goto_group, hud_group, block_group, entity_group)
    def add(self,*message,**args): #M# cause named after * doesn't work in python2.x
        """Entities have 2 Priority Levels (0: normal, 1: the player himself) for now"""
        priority = args.get("priority",0)
        group = self.group_of[message[0]][priority]
        group.add(message)

    def __iter__(self):
        # not round robin
        if False:
            for group in self.groups:
                while True:
                    m = group.pop()
                    if not m:
                        break
                    yield " ".join(str(part) for part in m)
            return
        # round robin
        last_hit = self.groups[-1]
        for group in itertools.cycle(self.groups):
            msg = group.pop()
            if msg != None:
                yield " ".join(str(part) for part in msg)
                last_hit = group
            elif last_hit == group: #eine Runde rum ohne was zu finden
                break
                

class Player(object):
    """a player/observer is someone how looks through the eyes of an entity"""
    RENDERDISTANCE = 16
    def __init__(self,renderlimit,initmessages=()):
        self.renderlimit = renderlimit
        self.entity = None
        self.outbox = MessageBuffer()
        for msg in initmessages:
            self.outbox.add(*msg)
        self.focus_distance = 0
        self.sentcount = 0 # number of msgs sent to player since he last sent something
        self.action_states = {}
        self.was_pressed_set = set()
        self.observed_chunks = set()
        self._lc = set() #load chunks
        self._uc = set() #unload chunks
        if self.renderlimit:
            thread.start_new_thread(self._update_chunks_loop,())
        self.quit_flag = False
        self.lock = thread.allocate_lock() # lock this while making changes to entity, observed_chunks, _lc, _uc
        self.lock_used = False             # and activate this to tell update_chunks_loop to dismiss changes
        
        self.hud_cache = {}

    def quit(self):
        self.quit_flag = True
        if self.entity:
            self.entity.set_world(None,(0,0,0)) #M# maybe just change texture to ghost so player can rejoin later?

    def observe(self,entity):
        self.lock.acquire()
        if self.entity:
            self.entity.observers.remove(self)
            old_world = self.entity.world
        else:
            old_world = None
        self.entity = entity
        entity.observers.add(self)
        self.lock_used = True
        self.lock.release()

        self._notice_world(old_world,entity.world)
        self._notice_position()

    def is_pressed(self,key):
        """return whether key is pressed """
        return self.action_states.get(key,False)

    def was_pressed(self,key):
        """return whether key was pressed since last update"""
        return key in self.was_pressed_set

    def is_active(self):
        """indicates whether client responds (fast enough)"""
        return self.sentcount >= 0

    def get_focused_pos(self,max_distance=None):
        """Line of sight search from current position. If a block is
        intersected it's position is returned, along with the face and distance:
            (distance, position, face)
        If no block is found, return (None, None, None).

        max_distance : How many blocks away to search for a hit.
        """ 
        if max_distance == None:
            max_distance = self.focus_distance
        return hit_test(lambda v:self.entity.world.get_block(v)["id"]!="AIR",self.entity["position"],
                        self.entity.get_sight_vector(),max_distance)
    
    def get_focused_entity(self,max_distance=None):
        #M# to be moved to entity!
        """Line of sight search from current position. If an entity is
        intersected it is returned, along with the distance.
        If no block is found, return (None, None).

        max_distance : How many blocks away to search for a hit."""
        if max_distance == None:
            max_distance = self.focus_distance
        nearest_entity = None
        ray = Ray(self.entity["position"],self.entity.get_sight_vector())
        for entity in self.entity.world.get_entities(): #M# limit considered entities
            if entity is self.entity:
                continue
            d = entity.HITBOX.raytest(entity["position"],ray)
            if (d != False) and (d < max_distance):
                nearest_entity = entity
                max_distance = d
        if nearest_entity:
            return max_distance, nearest_entity
        return (None, None)

    def set_focus_distance(self,distance):
        """Set maximum distance for focusing block"""
        self.outbox.add("focusdist","%g"%distance)
        self.focus_distance = distance

    def set_hud(self,element_id,texture,position,rotation,size,alignment):
        if texture == "AIR":
            self.del_hud(element_id)
            return
        if self.hud_cache.get(element_id,None) == (texture,position,rotation,size,alignment):
            return
        x,y,z = position; w,h = size
        self.outbox.add("sethud", element_id, texture, x, y, z, rotation, w, h, alignment)
        self.hud_cache[element_id] = (texture,position,rotation,size,alignment)

    def del_hud(self,element_id):
        if element_id in self.hud_cache:
            self.outbox.add("delhud", element_id)
            self.hud_cache.pop(element_id)

    def focus_hud(self):
        self.outbox.add("focushud")

    ### it follows a long list of private methods that make sure a player acts like one ###

    def _init_chunks(self):
        if not self.entity or not self.entity.world:
            return
        for chunk in self.entity.world.chunks.values():
            self._lc.add(chunk)
        if self.lock.acquire():
            self._lc = sorted(self._lc,key=self._chunk_priority_func,reverse=True)
            self.lock.release()
        else:
            print "locking error"

    def _update_chunks_loop(self):
        try:
            while True:
                self.lock_used = False
                # copy some attributes because function is used asynchron
                try:
                    while not self.entity or not self.entity.world:
                        time.sleep(0.1)
                    world = self.entity.world
                    position = self.entity["position"].normalize()
                    radius=self.RENDERDISTANCE
                    r = range(-radius,radius,1<<world.chunksize)+[radius]
                    chunks = set()
                    for dx in r:
                        for dy in r:
                            time.sleep(0.01)
                            for dz in r:
                                chunkpos = position+(dx,dy,dz)
                                chunk = world._get_chunk(chunkpos,load_on_miss = not DOASYNCLOAD)
                                if chunk == None:
                                    world._async_load_chunk(chunkpos)
                                elif chunk == "loading":
                                    pass
                                else:
                                    chunks.add(chunk)
                except:
                    if self.lock_used:
                        continue
                    else:
                        raise
                #M# don't do any unloads, because who needs them anyway I mean... do them if they are too far away
                uc = {} #self.observed_chunks.difference(chunks)
                lc = chunks.difference(self.observed_chunks)
                lc = sorted(lc,key=self._chunk_priority_func,reverse=True)
                if self.lock.acquire(False):
                    if not self.lock_used:
                        self._uc = uc
                        self._lc = lc
                    self.lock.release()
        except Exception as e:
            if "-debug" in sys.argv or not self.quit_flag:
                raise e

    def _update_chunks(self):
        # unload chunks
        if self._uc:
            chunk = self._uc.pop()
            if chunk in self.observed_chunks:
                self.observed_chunks.remove(chunk)
                chunk.observers.remove(self)
                self.outbox.add("delarea",chunk.position)
                for entity in chunk.get_entities():
                    self._del_entity(entity)
        # load chunks
        if self._lc:
            chunk = self._lc.pop()
            if not chunk in self.observed_chunks and chunk.is_fully_generated():
                self.observed_chunks.add(chunk)
                codec = [b.client_version() for b in chunk.block_codec]
                data = repr((codec,chunk.compressed_data))
                self.outbox.add("setarea",chunk.position,data)
                chunk.observers.add(self)
                for entity in chunk.get_entities():
                    self._set_entity(entity)

    def _chunk_priority_func(self,chunk):
        return self._priority_func(chunk.position<<chunk.chunksize)

    def _priority_func(self,position):
        dist = position+(Vector([1,1,1])<<(self.entity.world.chunksize-1))-self.entity["position"]
        return sum(map(abs,dist))

    def _update(self):
        """internal update method, automatically called by game loop"""
        self._update_chunks()
        self.was_pressed_set.clear()

    def _handle_input(self,msg):
        """do something so is_pressed and was_pressed work"""
        if msg.startswith("tick"):
            self.sentcount = int(msg.split(" ")[1])
        elif msg.startswith("rot"):
            x,y = map(float,msg.split(" ")[1:])
            self.entity["rotation"] = (x,y)
        elif msg.startswith("keys"):
            action_states = int(msg.split(" ")[1])
            for i,a in enumerate(ACTIONS):
                new_state = bool(action_states & (1<<(i+1)))
                if new_state and not self.is_pressed(a):
                    self.was_pressed_set.add(a)
                self.action_states[a] = new_state
        else:
            self.was_pressed_set.add(msg)

    def _notice_position(self):
        """set position of camera/player"""
        if self.entity["position"]:
            self.outbox.add("goto",*self.entity["position"])

    def _notice_world(self, old_world, new_world):
        """to be called when self.entity.world has changed """
        self.lock.acquire()
        if old_world:
            old_world.players.discard(self)
        for chunk in self.observed_chunks:
            chunk.observers.remove(self)
        self.observed_chunks.clear()
        self.outbox.add("clear")
        if new_world:
            new_world.players.add(self)
            self.outbox.add("chunksize", new_world.chunksize) #M# is that right here? Make sure it doesn't get reordered with setting of blocks
        self.lock_used = True
        self.lock.release()
        if not self.renderlimit:
            self._init_chunks()

        
    def _notice_block(self,position,block_data):
        """send blockinformation to client"""
        self.outbox.add("set", position, block_data.client_version())

    def _notice_new_chunk(self,chunk):
        if not self.renderlimit:
            if chunk not in self._lc:
                self._lc.append(chunk)

    def _set_entity(self,entity):
        priority = 1 if entity == self.entity else 0
        self.outbox.add("setentity",hash(entity),entity["texture"],entity["position"],*entity["rotation"], priority=priority)

    def _del_entity(self,entity):
        self.outbox.add("delentity",hash(entity))

class World(object):
    BlockClass = Block
    PlayerEntityClass = Entity
    def __init__(self, worldgenerators = [], filename = None, spawnpoint=(0,0,0), chunksize = 4, defaultblock = "AIR"):
        """create new World instance"""
        self.chunksize = chunksize
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

    def __setitem__(self, position, block_id):
        self.set_block(position, block_id)

    def get_block(self, position, minlevel = None, load_on_miss = True):
        """get ID of block at position

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

    def _get_chunk(self, position, minlevel = None, load_on_miss = True):
        """
        accepts floating point position
        (minlevel, load_on_miss see get_block)
        """
        if minlevel == None:
            minlevel = len(self.worldgenerators)
        chunkposition = position.normalize()>>self.chunksize
        chunk = self.chunks.get(chunkposition,None)
        if not chunk:
            if not load_on_miss:
                return None
            chunk = ServerChunk(self.chunksize,self,chunkposition)
            self.chunks[chunkposition] = chunk
        if chunk.initlevel < minlevel:
            if not load_on_miss:
                return None
            self._load_chunk(chunk,minlevel)
        return chunk

    def _load_chunk(self, chunk, minlevel, wait_if_locked=True):
        if minlevel > len(self.worldgenerators):
            raise ValueError("the requested initlevel %i cannot be provided" %minlevel)
        if not chunk.lock.acquire(wait_if_locked):
            return False
        if chunk.initlevel == -1:
            chunk.init_data()
            chunk.initlevel = 0
        while chunk.initlevel < minlevel:
            self.worldgenerators[chunk.initlevel](chunk)
            chunk.initlevel+=1
        chunk.lock.release()
        return True
        
    def _async_load_chunk(self, position):
        self.loading_queue.append(position)
        if self.load_thread_count < MAX_LOAD_THREADS:
            thread.start_new_thread(self._async_load_loop,())

    def _test_priority(self,position):
        """priority for generating new chunk based on position"""
        players = filter(lambda entity:isinstance(entity,Player),self.entities)
        if players:
            return min([player._priority_func(position) for player in players])
        return 0

    def _async_load_loop(self):
        self.load_thread_count += 1
        while self.loading_queue:
            try:
                position = min(self.loading_queue, key=self._test_priority)
                self.loading_queue.remove(position)
            except ValueError:
                continue
            self._get_chunk(position) # does exactly what we need so why don't use it
        self.load_thread_count -= 1
        return

    def get_entities(self):
        """return set of entities in world"""
        return self.entities
    
    def spawn_player(self,player):
        spielfigur = self.PlayerEntityClass()
        spielfigur.set_world(self,self.spawnpoint)
        player.observe(spielfigur)

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
                print "File %s not found." %filename

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

class Game(object):
    """
    Ein Game Objekt sorgt für die Kommunikation mit dem/den Klienten.
    Bei Mehrbenutzerprogrammen muss jeder Benutzer sich mittels des
    Programms voxelengine/client.py verbinden.

    Es ist empfehlenswert Game mit einem with Statement zu benutzen:
    >>> with Game(*args,*kwargs) as g:
    >>>     ...

    args (Argumente):
        spawnpoint : (world, (x,y,z)) where to place new players

    kwargs (optionale Argumente):
        init_function : function to call with new players (callback)
        wait          : wait for players to disconnect before leaving with statement
        multiplayer   : True  - open world to lan
                        False - open client with direct connection
        name          : name of the server
        (socket_server: only use this if you know what you're doing)

    (bei Benutzung ohne "with", am Ende unbedingt Game.quit() aufrufen)
    """

    def __init__(self,
                 init_function=lambda player:None,
                 wait=True,
                 name="MCG-CRAFT",
                 renderlimit=False,
                 suggested_texturepack="basic_colors",
                 PlayerClass=Player,
                 socket_server=None, #only use this if you know what you're doing
                 ):
        self.init_function = init_function
        self.wait = wait
        self.renderlimit = renderlimit
        self.suggested_texturepack = suggested_texturepack
        self.PlayerClass = PlayerClass

        self.players = {}
        self.new_players = set()

        if socket_server == None:
            import socket_connection_2 as socket_connection
            self.socket_server = socket_connection.server(key="voxelgame",on_connect=self._on_connect,
                                                          on_disconnect=self._on_disconnect,name=name)
        else:
            self.socket_server = socket_server
        if "-debug" in sys.argv:
            print "game ready"

    def __del__(self):
        pass

    def __enter__(self):
        """for use with "with" statement"""
        return self

    def __exit__(self,*args):
        """for use with "with" statement"""
        if args == (None,None,None): #kein Fehler aufgetreten
            while self.wait and self.get_players():
                self.update()
        self.quit()
    
    def quit(self):
        """quit the game"""
        self.socket_server.close()
        for player in self.players.values():
            if player:
                player.quit()

    def get_new_players(self):
        """get set of players connected since last call to this function"""
        ret = self.new_players
        self.new_players = set()
        return ret

    def get_players(self):
        """get a list of connected players"""
        return self.players.values()

    def _on_connect(self,addr):
        """place at worldspawn"""
        if "-debug" in sys.argv:
            print(addr, "connected")
        initmessages = [("setup",self.suggested_texturepack)]
        p = self.PlayerClass(self.renderlimit,initmessages)
        self.players[addr] = p
        self.new_players.add(p)
        self.init_function(p)

    def _on_disconnect(self,addr):
        if "-debug" in sys.argv:
            print(addr, "disconnected")
        # do something with player
        player = self.players.pop(addr)
        player.quit()

    def update(self):
        """communicate with clients
        call regularly to make sure internal updates are performed"""
        for addr,player in self.players.items():
            player.sentcount += 2 #make sure at least two massages are sent anyway: goto and setentity of own player
            for msg in player.outbox:
                player.sentcount -= 1
                self.socket_server.send(msg,addr)
                if player.sentcount <= 0:
                    break
        for player in self.get_players():
            player._update() #call to player._update() has to be before call to player._handle_input()
        for msg, addr in self.socket_server.receive():
            if addr in self.players:
                self.players[addr]._handle_input(msg)
            elif "-debug" in sys.argv:
                print "Message from unregistered Player"
        time.sleep(0.001) #wichtig damit das threading Zeug klappt
    
    def launch_client(self):
        import subprocess
        command = ["python",os.path.join(PATH,"client.py"),"--host=localhost","--port=%i" %self.socket_server.get_entry_port()]
        p = subprocess.Popen(command)


if __name__ == "__main__":
    def _simple_terrain_generator(chunk):
        """a very simple terrain generator -> flat map"""
        if chunk.position[1] >= 0:
            return # nothing to do in the sky by now
        for position in chunk:
            if position[1] < -2:
                if (position[0]+position[2]) % 2:
                    chunk.set_block(position,"GREEN")
                else:
                    chunk.set_block(position,"CYAN")

    w = World([_simple_terrain_generator])
    settings = {"init_function" : w.spawn_player,
                }
    with Game(**settings) as g:
        g.launch_client()
        while not g.get_players():
            g.update()
        w.set_block((-1,2,-3),"YELLOW")
