import math
import time
import thread

import socket_connection
reload(socket_connection)
from shared import *

DOASYNCLOAD = True
MAX_LOAD_THREADS = 1
MSGS_PER_TICK = 10

# TODO:
# deloading with bigger radius than loading
# (maybe add optional visibility filter to server)

# ABOUT:
# initlevels: (managing multi-chunk-structures)
# inf (finished): finished, Entities may be here, can be send to client, ...
#   4 (structs) : postmulti-single-chunk-structures
#   3 (structs) : multi-chunk-structures
#   2 (structs) : premulti-single-chunk-structures
#   1 (terrain) : terrain build
#   0 (plain)   : nothing generated yet
#  -1 (vacuum)  : not even air
# idea: every chunk may require chunks around him to be at a level of at least (his level - 1)


class _Chunkdict(dict):
    def __init__(self,world,*args,**kwargs):
        dict.__init__(self,*args,**kwargs)
        self.world = world

    def __missing__(self, chunkposition):
        chunk = ServerChunk(self.world,chunkposition)
        self[chunkposition] = chunk
        return chunk

class World(object):
    def __init__(self, worldgenerators = [], chunk_priority_func = None):
        self.worldgenerators = worldgenerators #[level1generation,level2generation,...]?
        self.chunk_priority_func = chunk_priority_func
        self.loading_queue = []
        self.load_thread_count = 0
        self.chunks = _Chunkdict(self)

    def __getitem__(self, position):
        return self.get_block(position)
    
    def __setitem__(self, position, block_id):
        self.set_block(position, block_id)

    def get_block(self, position, minlevel = None, load_on_miss = True):
        """
        minlevel and load_on_miss are passed to get_chunk...
        """
        chunk = self.get_chunk(position, minlevel, load_on_miss)
        if chunk == None:
            return None
        return chunk.get_block(position)

    def set_block(self, position, block_id, minlevel = None, load_on_miss = True):
        chunk = self.get_chunk(position, minlevel, load_on_miss)
        if chunk == None:
            return False
        chunk.set_block(position,block_id)
        for observer in chunk.observers:
            observer.notice(position,block_id)
        return True

    def get_chunk(self, position, minlevel = None, load_on_miss = True):
        """
        accepts floating point position
        """
        if minlevel == None:
            minlevel = len(self.worldgenerators)
        position = position.normalize()
        chunk = self.chunks[position>>CHUNKSIZE]
        if chunk.initlevel < minlevel:
            if not load_on_miss:
                return
            self.load_chunk(chunk,minlevel)
        return chunk

    def load_chunk(self, chunk, minlevel, wait_if_locked=True):
        if minlevel > len(self.worldgenerators):
            raise ValueError("the requested initlevel %i cannot be provided" %minlevel)
        if not chunk.lock.acquire(wait_if_locked):
            return False
        if chunk.initlevel == -1:
            if False: #M# try to load from file
                pass
            else: #fill with airblocks
                chunk.init_data()
            chunk.initlevel = 0
        while chunk.initlevel < minlevel:
            self.worldgenerators[chunk.initlevel](chunk)
            chunk.initlevel+=1
        chunk.lock.release()
        return True
        
    def async_load_chunk(self, position):
        self.loading_queue.append(position)
        if self.load_thread_count < MAX_LOAD_THREADS:
            thread.start_new_thread(self._async_load_loop,())

    def _async_load_loop(self):
        self.load_thread_count += 1
        while self.loading_queue:
            if self.chunk_priority_func:
                try:
                    position = min(self.loading_queue, key=self.chunk_priority_func)
                    self.loading_queue.remove(position)
                except ValueError:
                    continue
            else:
                try:
                    position = self.loading_queue.pop(0)
                except IndexError:
                    continue
            self.get_chunk(position) # does exactly what we need so why don't use it
        self.load_thread_count -= 1
        return

    def save(self):
        #M# doesn't work either
        for position,chunk in self.chunks.items():
            if chunk.altered:
                pass #do something savy and unload if without observers

class ServerChunk(Chunk):
    def __init__(self, world, position):
        self.world = world
        self.position = position # used for sending chunk to player
        self.observers = set() #if empty and chunk not altered, it should be removed
        self.entities = set()
        self.altered = False #M# not tracked yet
        self.initlevel = -1
        self.lock = thread.allocate_lock()

class Entity(object):
    SPEED = 5
    def __init__(self, world):
        self.world = world
        self.position = None
        self.rotation = None

    def set_position(self, position):
        #M# remove from chunk of old position & tell everyone
        self.position = position
        #M# add to chunk of new position & tell everyone

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

class Player(Entity):
    RENDERDISTANCE = 16
    spawnpoint = Vector([0,0,0])
    def __init__(self,world):
        Entity.__init__(self,world)
        self.outbox = []
        self.set_position(self.spawnpoint)
        self.rotation = (0,0)
        self.sentcount = 0 # number of msgs sent to player since he last sent something
        self.action_states = dict([(a,False) for a in ACTIONS])
        self.observed_chunks = set()
        self._lc = set()
        self._uc = set()
        thread.start_new_thread(self._update_chunks_loop,())
        self.last_update = time.time()

    def set_position(self,position):
        Entity.set_position(self,position)
        for msg in self.outbox:
            if msg.startswith("goto"):
                self.outbox.remove(msg)
        self.outbox.append("goto %s %s %s" %self.position)

    def _update_chunks_loop(self):
        try:
            while True:
                radius=self.RENDERDISTANCE
                position = self.position.normalize()
                chunks = set()
                for dx in range(-radius,radius,1<<CHUNKSIZE)+[radius]:
                    for dy in range(-radius,radius,1<<CHUNKSIZE)+[radius]:
                        time.sleep(0.01)
                        for dz in range(-radius,radius,1<<CHUNKSIZE)+[radius]:
                            chunkpos = position+(dx,dy,dz)
                            chunk = self.world.get_chunk(chunkpos,load_on_miss = not DOASYNCLOAD)
                            if chunk == None:
                                self.world.async_load_chunk(chunkpos)
                            elif chunk == "loading":
                                pass
                            else:
                                chunks.add(chunk)
                self._uc = self.observed_chunks.difference(chunks)
                lc = chunks.difference(self.observed_chunks)
                self._lc = sorted(lc,key=self._chunk_priority_func,reverse=True)
        except Exception as e:
            print("some error in _update_chunks_loop, most likely because the player disconnected, I should find a way to handle this nicely")

    def _update_chunks(self):
        # unload chunks
        if self._uc:
            chunk = self._uc.pop()
            if chunk in self.observed_chunks:
                self.observed_chunks.remove(chunk)
                chunk.observers.remove(self)
                self.outbox.append("delarea %s %s %s"
                               %(tuple(chunk.position)))
        # load chunks
        if self._lc:
            chunk = self._lc.pop()
            if not chunk in self.observed_chunks:
                self.observed_chunks.add(chunk)
                """
                startpos = None
                sequenz_id = 0
                count = 0
                for dy in range(1<<CHUNKSIZE):
                    for dx in range(1<<CHUNKSIZE):
                        for dz in range(1<<CHUNKSIZE):
                            b = chunk[Vector([dx,dy,dz])]
                            b_id = b.get_id() if b.get_visible() else 0
                            if b_id == sequenz_id:
                                count += 1
                            else:
                                if sequenz_id != 0:
                                    self.outbox.append("setarea %s %s %s %s %s %s"
                                        %(startpos[0],startpos[1],startpos[2],
                                          CHUNKSIZE,count,sequenz_id))
                                startpos = b.position
                                sequenz_id = b_id
                                count = 1
                """
                self.outbox.append("setarea %s %s %s "%(chunk.position[0],chunk.position[1],chunk.position[2])+chunk.compressed_data) #Send chunksize only once
                chunk.observers.add(self)

    def _chunk_priority_func(self,chunk):
        return self._priority_func(chunk.position<<CHUNKSIZE)

    def _priority_func(self,position):
        dist = position+(Vector([1,1,1])<<(CHUNKSIZE-1))+(self.position*-1)
        return sum(map(abs,dist))

    def _update(self):
        """internal update method, automatically called by game loop"""
        self._update_chunks()

    def handle_input(self,msg):
        """dummi method, replace in subclass, or monkeypatch Player class to allow input handling"""
        pass
        
    def notice(self,position,block_id):
        #position = block_interface.position
        #if block_interface.get_visible():
        self.outbox.append("set %s %s %s %s" %(position[0],position[1],position[2],block_id))
        #else:
        #    self.outbox.append("del %s %s %s" %(position[0],position[1],
        #                            position[2]))

class Game(object):

    def __init__(self,worldgenerators,name="MCG-CRAFT",gamename="",playerclass=Player,socket_server=None):
        self.playerclass = playerclass
        self.players = {}
        self.world = World(worldgenerators,self._test_priority)
        self.world[Vector([0,0,0])]
        if socket_server == None:
            self.socket_server = socket_connection.server(key="voxelgame",on_connect=self._on_connect,
                                                          on_disconnect=self._on_disconnect,name=name)
        else:
            self.socket_server = socket_server
            self._on_connect(None)
        print "ready"

    def __enter__(self):
        return self

    def __exit__(self,*args):
        self.quit()
    
    def quit(self):
        """quit the game"""
        self.socket_server.close()

    def get_players(self):
        """get a list of all players in the game"""
        return self.players.values()

    def _test_priority(self,position):
        """priority for generating new chunk based on position"""
        if self.players:
            return min([player._priority_func(position) for player in self.get_players()])
        return 0

    def _on_connect(self,addr):
        print(addr, "connected")
        self.players[addr] = self.playerclass(self.world)

    def _on_disconnect(self,addr):
        print(addr, "disconnected")
        # do something with player
        del self.players[addr]

    def update(self):
        #print "tick",time.time()
        """communicate with clients"""
        #send stuff
        #print 1
        for addr,player in self.players.items():
            while player.outbox:
                msg = player.outbox.pop(0)
                player.sentcount += 1
                self.socket_server.send(msg,addr)
                if player.sentcount >= MSGS_PER_TICK:
                    break
        #receive stuff
        #print 2
        for msg, addr in self.socket_server.receive():
            if addr in self.players:
                self.players[addr].handle_input(msg)
            else:
                print "Fehler"
        #internal player update
        #print 3
        for player in self.get_players():
            player._update()

def simple_terrain_generator(chunk):
    if chunk.position[1] >= 0:
        return # nothing to do in the sky by now
    for position in chunk:
        if chunk.position[1]*(1<<CHUNKSIZE)+position[1] <= -2:
            chunk.set_block(position,BLOCK_ID_BY_NAME["GRASS"])

if __name__ == "__main__":

    with Game([simple_terrain_generator]) as g:
        while True:
            g.update()
