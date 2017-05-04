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
import textures

DOASYNCLOAD = True
MAX_LOAD_THREADS = 1
MSGS_PER_TICK = 10
DEFAULT_SETUP_PATH = os.path.join(PATH,"setups","colors_setup.py")
setup = {"users":set()}

# merke: wenn man from voxelengine import * macht werden neue globale Variablen nach dem import nicht übernommen :(
# ergo: globale Variablen nicht mehr ändern zur Laufzeit (verändern der Objekte ist ok)

def load_setup(path):
    """
    Load a path to a setup file like the ones in voxelengine/setups directory.
    Make sure that the path is suitable for the client too,
    so be careful when using relative paths.
    """
    warn = False
    if setup["users"]:
        warn = True
    setupfile = open(path,"r")
    setup.clear()
    setup.update(ast.literal_eval(setupfile.read()))
    setup["users"] = set()
    setup["SETUP_PATH"] = path
    setup["BLOCK_ID_BY_NAME"] = {"AIR":0}
    setup["BLOCK_NAME_BY_ID"] = ["AIR"]
    setup["SOLIDITY"] = [False]
    for i, (name, transparency, solidity, sides) in enumerate(setup["TEXTURE_INFO"]):
        setup["BLOCK_ID_BY_NAME"][name] = i+1
        setup["BLOCK_NAME_BY_ID"].append(name)
        setup["SOLIDITY"].append(solidity)
    if warn:
        raise RuntimeWarning("You changed a setup that was currently used. (You can catch this warning but it will most likely crash your game.)")

load_setup(DEFAULT_SETUP_PATH)

class _Chunkdict(dict):
    def __init__(self,world,*args,**kwargs):
        dict.__init__(self,*args,**kwargs)
        self.world = world

    def __missing__(self, chunkposition):
        chunk = ServerChunk(self.world.chunksize,self.world,chunkposition)
        self[chunkposition] = chunk
        for player in self.world.players:
            player._notice_new_chunk(chunk)
        return chunk

class World(object):
    def __init__(self, worldgenerators = [], filename = None, spawnpoint=(0,0,0)):
        """create new World instance"""
        setup["users"].add(self)
        self.chunksize = setup["CHUNKSIZE"]
        self.worldgenerators = worldgenerators
        self.spawnpoint = Vector(spawnpoint)
        self.loading_queue = []
        self.load_thread_count = 0
        self.chunks = _Chunkdict(self)
        self.entities = set()
        self.players = set()
        if filename != None:
            self._load(filename)

    def __del__(self):
        try:
            setup["users"].remove(self)
        except:
            pass

    def __getitem__(self, position):
        return self.get_block(position)

    def __setitem__(self, position, block_id):
        self.set_block(position, block_id)

    def get_block_name(self,position):
        """get name of block at position

        in special cases you might consider using
        BLOCK_ID_BY_NAME[name] or BLOCK_NAME_BY_ID[id] for conversion"""
        block_id = self.get_block(position)
        #if not (0 <= block_id < len(setup["BLOCK_NAME_BY_ID"])):
        #    raise Exception("Can't find name for block id %i" %block_id)
        return setup["BLOCK_NAME_BY_ID"][block_id]

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

    def set_block_name(self, position, blockname):
        block_id = setup["BLOCK_ID_BY_NAME"][blockname]
        self.set_block(position, block_id)

    def set_block(self, position, block, minlevel = None, load_on_miss = True):
        """set block at position"""
        position = Vector(position)
        chunk = self._get_chunk(position, minlevel, load_on_miss)
        if chunk == None:
            return False
        chunk.set_block(position,block)
        for observer in chunk.observers:
            observer._notice_block(position,block)
        return True

    def _get_chunk(self, position, minlevel = None, load_on_miss = True):
        """
        accepts floating point position
        (minlevel, load_on_miss see get_block)
        """
        if minlevel == None:
            minlevel = len(self.worldgenerators)
        position = position.normalize()
        chunk = self.chunks[position>>self.chunksize]
        if chunk.initlevel < minlevel:
            if not load_on_miss:
                return
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
        chunk.altered = False #M# make this True if generated chunks should be saved (because generation uses random...)
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
        spielfigur = Entity()
        spielfigur.set_position(self.spawnpoint,self)
        player.observe(spielfigur)

    def _load(self,filename):
        if os.path.exists(filename):
            with zipfile.ZipFile(filename,"r",allowZip64=True) as zf:
                if zf.read("info_chunksize") != str(self.chunksize):
                    raise RuntimeError("It is currently not possible to load Worlds that were saved with another chunksize.")
                for name in zf.namelist():
                    if name.startswith("c"):
                        _,x,y,z = name.split("_")
                        position = Vector(map(int,(x,y,z)))
                        initlevel,compressed_data = zf.read(name).split(" ",1)
                        initlevel = int(initlevel)

                        c = ServerChunk(self.chunksize,self,position)
                        c.initlevel = initlevel
                        c.compressed_data = compressed_data
                        self.chunks[position] = c
        else:
            if "-debug" in sys.argv:
                print "File %s not found." %filename

    def save(self,filename):
        """not implemented yet"""
        with zipfile.ZipFile(filename,"w",allowZip64=True) as zf:
            zf.writestr("info_chunksize",str(self.chunksize))
            for position,chunk in self.chunks.items():
                if chunk.altered:
                    x,y,z = map(str,chunk.position)
                    name = "_".join(("c",x,y,z))
                    initlevel = str(chunk.initlevel)
                    data = " ".join((initlevel,chunk.compressed_data))
                    zf.writestr(name,data)


class ServerChunk(Chunk):
    """The (Server)Chunk class is only relevant when writing a world generator
    
    you can iterate over the positions in a chunk by:
    >>> for position in chunk:
    >>>     ...
    """
    def __init__(self, chunksize, world, position):
        Chunk.__init__(self,chunksize)
        self.world = world
        self.position = position # used for sending chunk to player
        self.observers = set() #if empty and chunk not altered, it should be removed
        self.initlevel = -1
        self.lock = thread.allocate_lock()

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
        if (position>>self.chunksize) == self.position:
            return Chunk.get_block(self,position)
        return self.world.get_block(position,self.initlevel-1)
    
    def set_block(self, position, block):
        """
        like normal Chunks set_block but
        - searches world if position is not within chunk (with own initlevel-1)
        - recommended for setting blocks of other chunks in terrain generators
        """
        if (position>>self.chunksize) == self.position:
            if isinstance(block,basestring):
                block = setup["BLOCK_ID_BY_NAME"][block]
            return Chunk.set_block(self,position,block)
        return self.world.set_block(position,block,self.initlevel-1)

    def get_block_name(self,position):
        """get name of block at position"""
        return setup["BLOCK_NAME_BY_ID"][self.get_block(position)]

    def get_entities(self):
        return (entity for entity in self.world.entities if (entity.position.normalize()>>self.chunksize) == self.position)

class TextureElement(object):
    def __init__(self,texture_id,x,y,z,dx,dy,dz):
        raise NotImplementedError()

class EntityModel(object):
    def __init__(self,*elements):
        """elements may be TextureElements (and hopefully someday EntityModels)"""
        self.elements = elements

class Entity(object):
    SPEED = 5
    def __init__(self):
        self.world = None
        self.position = None
        self.rotation = (0,0)
        self.observers = set()
        self.texture = 0

    def get_position(self):
        """return position of entity"""
        return self.position

    def set_position(self, position, world=None):
        """set position of entity"""
        # observer of this entity (the player)
        for observer in self.observers:
            observer._notice_position(position, world)
        #M# remove from chunk of old position & tell everyone
        old_observers = self.world._get_chunk(self.position).observers if self.world else set()
        changed_world = world and world != self.world
        if changed_world:
            if self.world:
                self.world.entities.discard(self)
            self.world = world
            self.world.entities.add(self)
        self.position = Vector(position)
        #M# add to chunk of new position & tell everyone
        new_observers = self.world._get_chunk(self.position).observers if self.world else set()
        for o in old_observers.difference(new_observers):
            o._del_entity(self)
        for o in new_observers:
            o._set_entity(self)

    def set_texture(self,texture):
        self.texture = texture
        self._inform_observers()

    def set_rotation(self, yaw, pitch):
        self.rotation = yaw,pitch
        self._inform_observers()

    def get_sight_vector(self):
        """ Returns the current line of sight vector indicating the direction
        the entity is looking.

        """
        x, y = self.rotation
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

    def _inform_observers(self):
        if self.world:
            for observer in self.world._get_chunk(self.position).observers:
                observer._set_entity(self)

class Player(object):
    """a player/observer is someone how looks through the eyes of an entity"""
    RENDERDISTANCE = 16
    def __init__(self,initmessages=()):
        self.entity = None
        self.outbox = []
        self.outbox.extend(initmessages)
        self.focus_distance = setup["DEFAULT_FOCUS_DISTANCE"]
        self.sentcount = 0 # number of msgs sent to player since he last sent something
        self.action_states = {}
        self.was_pressed_set = set()
        self.observed_chunks = set()
        self._lc = set() #load chunks
        self._uc = set() #unload chunks
        if setup["RENDERLIMIT"]:
            thread.start_new_thread(self._update_chunks_loop,())
        else:
            self._init_chunks()
        self.lock = thread.allocate_lock() # lock this while making changes to entity, observed_chunks, _lc, _uc
        self.lock_used = False             # and activate this to tell update_chunks_loop to dismiss changes

    def observe(self,entity):
        self._notice_position(entity.position,entity.world)
        self.lock.acquire()
        if self.entity:
            self.entity.observers.remove(self)
        self.entity = entity
        entity.observers.add(self)
        self.lock_used = True
        self.lock.release()
        if not setup["RENDERLIMIT"]:
            self._init_chunks()

    def is_pressed(self,key):
        """return whether key is pressed """
        return self.action_states.get(key,False)

    def was_pressed(self,key):
        """return whether key was pressed since last update"""
        return key in self.was_pressed_set

    def is_active(self):
        """indicates whether client responds (fast enough)"""
        return self.sentcount <= MSGS_PER_TICK

    def get_focused_pos(self,max_distance=None):
        """Line of sight search from current position. If a block is
        intersected it is returned, along with the block previously in the line
        of sight. If no block is found, return (None, None).

        max_distance : How many blocks away to search for a hit.
        """ 
        if max_distance == None:
            max_distance = self.focus_distance
        return hit_test(lambda v:self.entity.world.get_block(v)!=0,self.entity.position,
                        self.entity.get_sight_vector(),max_distance)

    def set_focus_distance(self,distance):
        """Set maximum distance for focusing block"""
        self.outbox.append("focusdist %g" %distance)
        self.focus_distance = distance

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
    ### it follows a long list of private methods that make sure a player acts like one ###
    def _update_chunks_loop(self):
        try:
            while True:
                self.lock_used = False
                # copy some attributes because function is used asynchron
                try:
                    while not self.entity or not self.entity.world:
                        time.sleep(0.1)
                    world = self.entity.world
                    position = self.entity.position.normalize()
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
                uc = self.observed_chunks.difference(chunks)
                lc = chunks.difference(self.observed_chunks)
                lc = sorted(lc,key=self._chunk_priority_func,reverse=True)
                if self.lock.acquire(False):
                    if not self.lock_used:
                        self._uc = uc
                        self._lc = lc
                    self.lock.release()
        except Exception as e:
            raise
            #M#
            #try:
            #    raise
            #except:
            #    pass

    def _update_chunks(self):
        # unload chunks
        if self._uc:
            chunk = self._uc.pop()
            if chunk in self.observed_chunks:
                self.observed_chunks.remove(chunk)
                chunk.observers.remove(self)
                self.outbox.append("delarea %s %s %s"
                               %(tuple(chunk.position)))
                for entity in chunk.get_entities():
                    self._del_entity(entity)
        # load chunks
        if self._lc:
            chunk = self._lc.pop()
            if not chunk in self.observed_chunks:
                self.observed_chunks.add(chunk)
                self.outbox.append("setarea %s %s %s "%(chunk.position[0],chunk.position[1],chunk.position[2])+chunk.compressed_data) #Send chunksize only once
                chunk.observers.add(self)
                for entity in chunk.get_entities():
                    self._set_entity(entity)

    def _chunk_priority_func(self,chunk):
        return self._priority_func(chunk.position<<chunk.chunksize)

    def _priority_func(self,position):
        dist = position+(Vector([1,1,1])<<(self.entity.world.chunksize-1))-self.entity.position
        return sum(map(abs,dist))

    def _update(self):
        """internal update method, automatically called by game loop"""
        self._update_chunks()
        self.was_pressed_set.clear()

    def _handle_input(self,msg):
        """do something so is_pressed and was_pressed work"""
        if msg == "tick":
            self.sentcount = 0
        if msg.startswith("rot"):
            x,y = map(float,msg.split(" ")[1:])
            self.entity.set_rotation(x,y)
        if msg in ("right click","left click"):
            self.was_pressed_set.add(msg)
        if msg.startswith("keys"):
            action_states = int(msg.split(" ")[1])
            for i,a in enumerate(ACTIONS):
                new_state = bool(action_states & (1<<(i+1)))
                if new_state and not self.is_pressed(a):
                    self.was_pressed_set.add(a)
                self.action_states[a] = new_state

    def _notice_position(self,position,world):
        """set position of camera/player"""
        if world != None and (not self.entity or world != self.entity.world):
            if self.entity and self.entity.world:
                self.entity.world.players.discard(self)
            if world:
                world.players.add(self)
            self.lock.acquire()
            for chunk in self.observed_chunks:
                chunk.observers.remove(self)
            self.observed_chunks.clear()
            self.outbox.append("clear")
            self.lock_used = True
            self.lock.release()
        self.outbox[:] = (msg for msg in self.outbox if not msg.startswith("goto"))
        self.outbox.insert(0,"goto %s %s %s" %position)

    def _notice_block(self,position,block):
        """send blockinformation to client"""
        if isinstance(block,basestring):
                block = setup["BLOCK_ID_BY_NAME"][block]
        self.outbox.append("set %s %s %s %s" %(position[0],position[1],position[2],block))

    def _notice_new_chunk(self,chunk):
        if not setup["RENDERLIMIT"]:
            if chunk not in self._lc:
                self._lc.append(chunk)

    def _set_entity(self,entity):
        new_msg = "setentity %s %s %s %s %s %s %s" %(hash(entity),entity.texture,entity.position[0],entity.position[1],entity.position[2],entity.rotation[0],entity.rotation[1])
        for i,msg in enumerate(self.outbox):
            if msg.startswith("setentity %s" %hash(entity)):
                self.outbox[i] = new_msg
                break
        else:
            self.outbox.append(new_msg)

    def _del_entity(self,entity):
        self.outbox.append("delentity %s" %hash(entity))

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
                 init_function=None,
                 wait=True,
                 multiplayer=False,
                 name="MCG-CRAFT",
                 socket_server=None, #only use this if you know what you're doing
                 ):
        setup["users"].add(self)
        self.init_function = init_function
        self.wait = wait

        self.players = {}
        self.new_players = set()
        #M# set priority function somewhere self.world = World(worldgenerators,self._test_priority)
        #M# why?: self.world[Vector([0,0,0])]
        if socket_server == None:
            if multiplayer:
                import socket_connection
                self.socket_server = socket_connection.server(key="voxelgame",on_connect=self._on_connect,
                                                              on_disconnect=self._on_disconnect,name=name)
            else:
                def singleplayer_client_thread(socket_client):
                    import client
                    client.main(socket_client)
                    self._on_disconnect(None)
                import local_connection
                connector = local_connection.Connector()
                thread.start_new_thread(singleplayer_client_thread,(connector.client,))
                self.socket_server = connector.server
                self._on_connect(None)
        else:
            self.socket_server = socket_server
        if "-debug" in sys.argv:
            print "game ready"

    def __del__(self):
        try:
            setup["users"].remove(self)
        except:
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
        initmessages = ["setup "+setup["SETUP_PATH"]]
        p = Player(initmessages)
        self.players[addr] = p
        self.new_players.add(p)
        self.init_function(p)

    def _on_disconnect(self,addr):
        if "-debug" in sys.argv:
            print(addr, "disconnected")
        # do something with player
        del self.players[addr]

    def update(self):
        """communicate with clients
        call regularly to make sure internal updates are performed"""
        for addr,player in self.players.items():
            while player.outbox:
                msg = player.outbox.pop(0)
                player.sentcount += 1
                self.socket_server.send(msg,addr)
                if player.sentcount >= MSGS_PER_TICK:
                    break
        for player in self.get_players():
            player._update() #call to player._update() has to be before call to player._handle_input()
        for msg, addr in self.socket_server.receive():
            if addr in self.players:
                self.players[addr]._handle_input(msg)
            elif "-debug" in sys.argv:
                print "Message from unregistered Player"
        time.sleep(0.01) #wichtig damit das threading Zeug klappt

def terrain_generator_from_heightfunc(heightfunc,block_id):
    """heightfunc(int,int)->int is used to create generator function
    (can be used as decorator)"""
    def terrain_generator(chunk):
        x,y,z = chunk.position<<chunk.chunksize
        c = 1 << chunk.chunksize
        r = xrange(c)
        for dx in r:
            for dz in r:            
                h = int(heightfunc(x+dx,z+dz))
                if y <= h:
                    if h < y+c:
                        i = chunk.pos_to_i(Vector([dx,h,dz]))
                        n = (h-y)
                    else:
                        i = chunk.pos_to_i(Vector([dx,c-1,dz]))
                        n = c-1
                    chunk[i-n*c:i+1:c] = block_id
    return terrain_generator

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
                "multiplayer": False,
                }
    with Game(**settings) as g:
        w.set_block((-1,2,-3),"YELLOW")
