import math
import time
import thread

import socket_connection
reload(socket_connection)
from shared import *

CHUNKSIZE = 3 # (in bit -> length is 2**CHUNKSIZE)
RENDERDISTANCE = 16
SPEED = 5

DIMENSION = 3
DOASYNCLOAD = True
MAX_LOAD_THREADS = 1
MSGS_PER_TICK = 10

class _Chunkdict(dict):
    def __missing__(position):
        chunk = Chunk()
        self[position] = chunk
        return chunk

class World(object):
    def __init__(self, worldgenerators = [], chunk_priority_func = None):
        self.worldgenerators = worldgenerators #[level1generation,level2generation,...]?
        self.chunk_priority_func = chunk_priority_func
        self.loading_queue = []
        self.load_thread_count = 0
        self.chunks = _Chunkdict()

    def __getitem__(self, position):
        return self.get_block(position)

    def get_block(self, position, level = float("inf"), wait = True): # required level, onmiss ("load","asyncload","none")
        """
        generate and wait are passed to get_chunk...
        """
        chunk = self.get_chunk(position, generate, wait)
        if chunk not in ("loading",None):
            return chunk[position]

    def get_chunk(self, position, generate = True, wait = True):
        """
        accepts floating point position
        generate ... whether to generate chunk if it isn't yet
        """
        position = position.normalize()
        try:
            while True:
                chunk = self.chunks[position>>CHUNKSIZE]
                if chunk != "async_loading":
                    break
                if not wait:
                    return "loading"
                time.sleep(0.05)
        except KeyError:
            if not generate:
                return None
            chunk = self.load_chunk(position)
        return chunk

    def load_chunk(self, position):
        chunk = Chunk(self, position>>CHUNKSIZE)
        self.worldgenerator(chunk)
        self.chunks[position>>CHUNKSIZE] = chunk
        return chunk

    def async_load_chunk(self, position):
        self.chunks[position>>CHUNKSIZE] = "async_loading"
        self.loading_queue.append(position)
        if self.load_thread_count < MAX_LOAD_THREADS:
            thread.start_new_thread(self._async_load_loop,())

    def _async_load_loop(self):
        self.load_thread_count += 1
        while self.loading_queue:
            if self.chunk_priority_func:
                position = min(self.loading_queue, key=self.chunk_priority_func)
                try:
                    self.loading_queue.remove(position)
                except ValueError:
                    continue
            else:
                try:
                    position = self.loading_queue.pop(0)
                except IndexError:
                    continue
            self.load_chunk(position)
        self.load_thread_count -= 1
        return

    def save(self):
        for position,chunk in self.chunks.items():
            if chunk.altered:
                pass #do something savy and unload if without observers

# think about how to handle empty chunks
# initlevels: (managing multi-chunk-structures)
# inf (finished): finished, Entities may be here, can be send to client, ...
#   4 (structs) : postmulti-single-chunk-structures
#   3 (structs) : multi-chunk-structures
#   2 (structs) : premulti-single-chunk-structures
#   1 (terrain) : terrain build
#   0 (plain)   : nothing generated yet
# idea: every chunk may require chunks around him to be at a level >= (his level - 1)

class Chunk(object):
    def __init__(self,world,position):
        self.world = world
        self.position = position
        #self.blocks = tuple([BlockData() for _ in xrange((1<<CHUNKSIZE)**DIMENSION)])
        self.blocks = None
        self.observers = set() #if empty and chunk not altered, it should be removed
        self.entities = set()
        self.altered = False
        self.initlevel = None

    def __iter__(self):
        for dx in range(1<<CHUNKSIZE):
            for dy in range(1<<CHUNKSIZE):
                for dz in range(1<<CHUNKSIZE):
                    yield self[Vector([dx,dy,dz])]

    def __getitem__(self, position):
        position = position%(1<<CHUNKSIZE)
        i = reduce(lambda x,y:(x<<CHUNKSIZE)+y,position)
        data = self.blocks[i]
        return BlockInterface(data,self,(self.position<<CHUNKSIZE)+position)

class _BlockData(object):
    def __init__(self):
        self.visible = None
        self.id = 0

NEIGHBOURS = [Vector([ 1, 0, 0]),
              Vector([ 0, 1, 0]),
              Vector([ 0, 0, 1]),
              Vector([-1, 0, 0]),
              Vector([ 0,-1, 0]),
              Vector([ 0, 0,-1])]

class BlockInterface(object):
    def __init__(self, data, chunk, position):
        self.data = data
        self.chunk = chunk
        self.position = position

    def get_id(self):
        return self.data.id

    def set_id(self, new_id):
        self.set_visible(False)
        self.data.id = new_id
        self.chunk.altered = True
        if not self.chunk.isinit:
            return
        for dn in NEIGHBOURS+[Vector([0,0,0])]:
            b = self.chunk.world.__getitem__(self.position+dn,False)
            if b:
                b.update_visibility()

    def _get_visible(self):
        if self.data.visible == None:
            self.data.visible = False
            self.update_visibility()
        return self.data.visible

    def _set_visible(self, visible):
        if self.data.visible != visible:
            self.data.visible = visible
            for observer in self.chunk.observers:
                observer.notice(self)

    def _update_visibility(self):
        visible = False
        if self.get_id() != 0:
            for dn in NEIGHBOURS:
                b = self.chunk.world.__getitem__(self.position+dn,False)
                if b and b.get_id() == 0:
                    visible = True
        self.set_visible(visible)

class Entity(object):
    def __init__(self, world):
        self.world = world
        self.position = None
        self.rotation = None
        self.speed = SPEED

    def set_position(self, position):
        #remove from chunk of old position
        self.position = position
        #add to chunk of new position

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
    def __init__(self,world):
        Entity.__init__(self,world)
        self.inbox = []
        self.outbox = []
        self.set_position(Vector([128,0,0]))
        self.rotation = (0,0)
        self.sentcount = 0 # number of msgs sent to player since he last sent something
        self.action_states = dict([(a,False) for a in ACTIONS])
        self.observed_chunks = set()
        self.lc = set()
        self.uc = set()
        thread.start_new_thread(self._update_chunks_loop,())
        self.last_update = time.time()

    def set_position(self,position):
        Entity.set_position(self,position)
        self.outbox.append("goto %s %s %s" %self.position)

    def _update_chunks_loop(self):
        while True:
            radius=RENDERDISTANCE
            position = self.position.normalize()
            chunks = set()
            for dx in range(-radius,radius,1<<CHUNKSIZE)+[radius]:
                for dy in range(-radius,radius,1<<CHUNKSIZE)+[radius]:
                    time.sleep(0.01)
                    for dz in range(-radius,radius,1<<CHUNKSIZE)+[radius]:
                        chunkpos = position+(dx,dy,dz)
                        chunk = self.world.get_chunk(chunkpos,not DOASYNCLOAD)
                        if chunk == None:
                            self.world.async_load_chunk(chunkpos)
                        elif chunk == "loading":
                            pass
                        else:
                            chunks.add(chunk)
            self.uc = self.observed_chunks.difference(chunks)
            lc = chunks.difference(self.observed_chunks)
            self.lc = sorted(lc,key=self.chunk_priority_func,reverse=True)

    def update_chunks(self):
        # unload chunks
        if self.uc:
            chunk = self.uc.pop()
            if chunk in self.observed_chunks:
                self.observed_chunks.remove(chunk)
                chunk.observers.remove(self)
                self.outbox.append("delarea %s %s %s %s"
                               %((1<<CHUNKSIZE,)+tuple(chunk.position<<CHUNKSIZE)))
        # load chunks
        if self.lc:
            chunk = self.lc.pop()
            if not chunk in self.observed_chunks:
                self.observed_chunks.add(chunk)
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
                chunk.observers.add(self)

    def _chunk_priority_func(self,chunk):
        return self.priority_func(chunk.position<<CHUNKSIZE)

    def priority_func(self,position):
        dist = position+(Vector([1,1,1])<<(CHUNKSIZE-1))+(self.position*-1)
        return sum(map(abs,dist))

    def handle(self,cmd):
        if cmd == "tick":
            self.sentcount = 0
        if cmd == "right click":
            v = hit_test(lambda v:self.world[v].get_id()!=0,self.position,
                         self.get_sight_vector())[1]
            if v:
                self.world[v].set_id("GRASS")
        if cmd == "left click":
            v = hit_test(lambda v:self.world[v].get_id()!=0,self.position,
                         self.get_sight_vector())[0]
            if v:
                self.world[v].set_id(0)
        if cmd.startswith("rot"):
            x,y = map(float,cmd.split(" ")[1:])
            self.rotation = x,y
        if cmd.startswith("keys"):
            action_states = int(cmd.split(" ")[1])
            for i,a in enumerate(ACTIONS):
                self.action_states[a] = bool(action_states & (1<<(i+1)))

    def update(self):
        # react to input
        while self.inbox:
            self.handle(self.inbox.pop(0))
        # Movement
        ds = min(1,SPEED*(time.time()-self.last_update))
        self.last_update = time.time()
        vx,vy,vz = self.get_sight_vector()*ds
        mx,my,mz = 0,0,0
        if self.sentcount <= MSGS_PER_TICK:
            if self.action_states["for"]:
                mx += vx; mz += vz
            if self.action_states["back"]:
                mx -= vx; mz -= vz
            if self.action_states["right"]:
                mx -= vz; mz += vx
            if self.action_states["left"]:
                mx += vz; mz -= vx
        self.set_position(self.position+(mx,my,mz))
        self.update_chunks()
        
    def notice(self,block_interface):
        position = block_interface.position
        if block_interface.get_visible():
            self.outbox.append("set %s %s %s %s" %(position[0],position[1],
                                    position[2],block_interface.get_id()))
        else:
            self.outbox.append("del %s %s %s" %(position[0],position[1],
                                    position[2]))

class Game(object):

    def __init__(self,worldgenerators,name="MCG-CRAFT",playerclass=Player):
        self.playerclass = playerclass
        self.players = {}
        self.world = World(worldgenerators,self._test_priority)
        self.socket_server = socket_connection.server(key="MCG_CRAFT",on_connect=self._on_connect,
                                                      on_disconnect=self._on_disconnect,name=name)

    def __enter__(self):
        return self

    def __exit__(self):
        self.quit()
    
    def quit(self)
        """quit the game"""
        self.socket_server.close()

    def get_players(self):
        """get a list of all players in the game"""
        return self.players.values()

    def test_priority(self,position):
        """priority for generating new chunk based on position"""
        if self.players:
            return min([player.priority_func(position) for player in self.get_players()])
        return 0

    def _on_connect(self,addr):
        print(addr, "connected")
        self.players[addr] = playerclass(self.world)

    def _on_disconnect(self,addr):
        print(addr, "disconnected")
        # do something with player
        del self.players[addr]

    def update(self):
        """communicate with clients"""
        for msg, addr in self.server_socket.receive():
            if addr in players:
                players[addr].inbox.append(msg)
            else:
                print "Fehler"
        for addr,player in players.items():
            while player.outbox:
                msg = player.outbox.pop(0)
                player.sentcount += 1
                server.send(msg,addr)
                if player.sentcount >= MSGS_PER_TICK:
                    break

if __name__ == "__main__":
    def wg1(chunk):
        # remember: I think it would be a bad idea to use block.set_id in here
        if chunk.position[1] >= 1:
            return # nothing to do in the sky by now
        for block in chunk:
            if block.position[1] < -2:
                block.set_id("GRASS")

    with Game([wg1]) as g:
        while True:
            g.update():
            for player in g.get_players():
                player.update()
