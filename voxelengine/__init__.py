#* encoding: utf-8 *#

# voxelengine: a pyglet based voxel engine module for Python
#
# Copyright (C) 2015 - 2016  Joram Brenz
# email: joram.brenz@online.de
#
# This software is provided 'as-is', without any express or implied
# warranty.  In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.


"""
a pyglet based voxel engine module for Python

Dieses Modul soll eine einfache Möglichkeit bieten um 3D/Würfel basierte
Programme zu schreiben.

This module is designed to provide a simple interface for 3D voxel based
applications.

Beispiel/Example:
>>> import voxelengine
>>> w = voxelengine.World()
>>> with voxelengine.Game( spawnpoint=(w,(0,0,0)) ) as g:
>>>     w.set_block((1,2,3),"GRASS")

"""

__version__ = '0.1.0'


import math
import time
import thread

import sys,os,inspect
# Adding directory modules to path
PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.append(os.path.join(PATH,"modules"))

from shared import *

DOASYNCLOAD = True
MAX_LOAD_THREADS = 1
MSGS_PER_TICK = 10

# TODO:
# players attribut für welt -> für ladepriorität benutzen
# change order of xyz to yxz in Chunkformat
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
    def __init__(self, worldgenerators = []):
        """create new World instance"""
        self.worldgenerators = worldgenerators
        self.loading_queue = []
        self.load_thread_count = 0
        self.chunks = _Chunkdict(self)
        self.entities = set()
        self.players = set()

    def __getitem__(self, position):
        return self.get_block(position)

    def __setitem__(self, position, block_id):
        self.set_block(position, block_id)

    def get_block(self, position, minlevel = None, load_on_miss = True):
        """ get ID of block at position

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

    def set_block(self, position, block_id, minlevel = None, load_on_miss = True):
        """set ID of block at position"""
        position = Vector(position)
        chunk = self._get_chunk(position, minlevel, load_on_miss)
        if chunk == None:
            return False
        chunk.set_block(position,block_id)
        for observer in chunk.observers:
            observer._notice(position,block_id)
        return True

    def _get_chunk(self, position, minlevel = None, load_on_miss = True):
        """
        accepts floating point position
        (minlevel, load_on_miss see get_block)
        """
        if minlevel == None:
            minlevel = len(self.worldgenerators)
        position = position.normalize()
        chunk = self.chunks[position>>CHUNKSIZE]
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
        
    def _async_load_chunk(self, position):
        self.loading_queue.append(position)
        if self.load_thread_count < MAX_LOAD_THREADS:
            thread.start_new_thread(self._async_load_loop,())

    def _test_priority(self,position):
        """priority for generating new chunk based on position"""
        players = filter(lambda entity:isinstance(entity,Player),self.entities)
        if players:
            return min([player._priority_func(position) for player in players])
        print "oh no!"
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

    def save(self):
        """not implemented yet"""
        raise NotImplementedError()
        #M# doesn't work either
        for position,chunk in self.chunks.items():
            if chunk.altered:
                pass #do something savy and unload if without observers

class ServerChunk(Chunk):
    """The (Server)Chunk class is only relevant when writing a world generator
    
    you can iterate over the positions in a chunk by:
    >>> for position in chunk:
    >>>     ...
    """
    def __init__(self, world, position):
        self.world = world
        self.position = position # used for sending chunk to player
        self.observers = set() #if empty and chunk not altered, it should be removed
        self.entities = set() #M# not up to date yet
        self.altered = False #M# not tracked yet
        self.initlevel = -1
        self.lock = thread.allocate_lock()

    def __iter__(self):
        """iterate over positions in chunk"""
        p = self.position<<CHUNKSIZE
        for dx in range(1<<CHUNKSIZE):
            for dy in range(1<<CHUNKSIZE):
                for dz in range(1<<CHUNKSIZE):
                    yield p+(dx,dy,dz)

class Entity(object):
    SPEED = 5
    def __init__(self):
        self.world = None
        self.position = None
        self.rotation = None

    def get_position(self):
        """return position of entity"""
        return self.position

    def set_position(self, position, world=None):
        """set position of entity"""
        #M# remove from chunk of old position & tell everyone
        if world and world != self.world:
            if self.world:
                self.world.entities.discard(self)
            self.world = world
            self.world.entities.add(self)
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

    def get_focused_pos(self,max_distance=8):
        """ Line of sight search from current position. If a block is
        intersected it is returned, along with the block previously in the line
        of sight. If no block is found, return (None, None).

        max_distance : How many blocks away to search for a hit.
        """ 
        return hit_test(lambda v:self.world.get_block(v)!=0,self.position,
                        self.get_sight_vector())

class Player(Entity):
    """a player is an Entity with some additional methods"""
    RENDERDISTANCE = 16
    def __init__(self,world,spawnpoint):
        Entity.__init__(self)
        self.outbox = []
        self.rotation = (0,0)
        self.sentcount = 0 # number of msgs sent to player since he last sent something
        self.action_states = {}
        self.was_pressed_set = set()
        self.observed_chunks = set()
        self._lc = set()
        self._uc = set()
        self.set_position(Vector(spawnpoint),world)
        thread.start_new_thread(self._update_chunks_loop,())

    def set_position(self,position,world=None):
        """set position of camera/player"""
        if world and world != self.world:
            #clear observed chunks if entering new world
            for chunk in self.observed_chunks:
                chunk.observers.remove(self)
            self.observed_chunks.clear()
            self.outbox.append("clear")
        Entity.set_position(self,position,world)
        for msg in self.outbox:
            if msg.startswith("goto"):
                self.outbox.remove(msg)
        self.outbox.append("goto %s %s %s" %self.position)

    def is_pressed(self,key):
        """return whether key is pressed """
        return self.action_states.get(key,False)

    def was_pressed(self,key):
        """return whether key was pressed since last update"""
        return key in self.was_pressed_set

    def is_active(self):
        """indicates whether client responds (fast enough)"""
        return self.sentcount <= MSGS_PER_TICK

    # it follows a long list of private methods that make sure a player acts like one
    def _update_chunks_loop(self):
        try:
            while True:
                # copy some attributes because function is used asynchron
                world = self.world
                position = self.position.normalize()
                radius=self.RENDERDISTANCE
                if not world:
                    time.sleep(0.1)
                    continue
                chunks = set()
                for dx in range(-radius,radius,1<<CHUNKSIZE)+[radius]:
                    for dy in range(-radius,radius,1<<CHUNKSIZE)+[radius]:
                        time.sleep(0.01)
                        for dz in range(-radius,radius,1<<CHUNKSIZE)+[radius]:
                            chunkpos = position+(dx,dy,dz)
                            chunk = world._get_chunk(chunkpos,load_on_miss = not DOASYNCLOAD)
                            if chunk == None:
                                world._async_load_chunk(chunkpos)
                            elif chunk == "loading":
                                pass
                            else:
                                chunks.add(chunk)
                self._uc = self.observed_chunks.difference(chunks)
                lc = chunks.difference(self.observed_chunks)
                self._lc = sorted(lc,key=self._chunk_priority_func,reverse=True)
        except Exception as e:
            raise
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
        self.was_pressed_set.clear()

    def _handle_input(self,msg):
        """do something so is_pressed and was_pressed work"""
        if msg == "tick":
            self.sentcount = 0
        if msg.startswith("rot"):
            x,y = map(float,msg.split(" ")[1:])
            self.rotation = x,y
        if msg in ("right click","left click"):
            self.was_pressed_set.add(msg)
        if msg.startswith("keys"):
            action_states = int(msg.split(" ")[1])
            for i,a in enumerate(ACTIONS):
                new_state = bool(action_states & (1<<(i+1)))
                if new_state and not self.is_pressed(a):
                    self.was_pressed_set.add(a)
                self.action_states[a] = new_state


    def _notice(self,position,block_id):
        """send blockinformation to client"""
        self.outbox.append("set %s %s %s %s" %(position[0],position[1],position[2],block_id))

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
        wait       : wait for players to disconnect before leaving with
        multiplayer: True  - open world to lan
                     False - open client with direct connection
        texturepath: specify path to custom texture.png
        textureinfo: see voxelengine/multiplayer/texture.py
        name       : name of the server
        (socket_server : only use this if you know what you're doing)

    (bei Benutzung ohne "with", am Ende unbedingt Game.quit() aufrufen)
    """

    def __init__(self,
                 spawnpoint,
                 wait=True,
                 multiplayer=False,
                 texturepath=None,
                 textureinfo=None,
                 name="MCG-CRAFT",
                 socket_server=None, #only use this if you know what you're doing
                 ):
        self.spawnpoint = spawnpoint
        self.wait = wait
        self.texturepath = texturepath
        self.textureinfo = textureinfo

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
        print "ready"

    def __enter__(self):
        """for use with "with" statement"""
        return self

    def __exit__(self,*args):
        """for use with "with" statement"""
        while self.wait and self.get_players():
            self.update()
            time.sleep(0.01) #wichtig damit das threading Zeug klappt
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
        print(addr, "connected")
        self.players[addr] = Player(*self.spawnpoint)
        self.new_players.add(Player)

    def _on_disconnect(self,addr):
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
            else:
                print "Fehler"
        time.sleep(0.01) #wichtig damit das threading Zeug klappt

def _simple_terrain_generator(chunk):
    """a very simple terrain generator -> flat map"""
    if chunk.position[1] >= 0:
        return # nothing to do in the sky by now
    for position in chunk:
        if position[1] < -2:
            chunk.set_block(position,BLOCK_ID_BY_NAME["GRASS"])

def terrain_generator_from_heightfunc(heightfunc):
    """does what it is called - can be used as decorator"""
    def terrain_generator(chunk):
        x,y,z = chunk.position<<CHUNKSIZE
        for dx in xrange(1<<CHUNKSIZE):
            for dz in xrange(1<<CHUNKSIZE):            
                h = int(heightfunc(x+dx,z+dz))
                if y <= h:
                    if h < y+(1<<CHUNKSIZE):
                        i = chunk.pos_to_i(Vector([dx,h,dz]))
                        n = (h-y)
                    else:
                        i = chunk.pos_to_i(Vector([dx,(1<<CHUNKSIZE)-1,dz]))
                        n = (1<<CHUNKSIZE)-1
                    chunk[i-n*(1<<CHUNKSIZE):i+1:1<<CHUNKSIZE] = BLOCK_ID_BY_NAME["GRASS"]
    return terrain_generator

if __name__ == "__main__":

    w = World([_simple_terrain_generator])
    settings = {"spawnpoint" : (w,(0,0,0)),
                "multiplayer": False,
                }
    with Game(**settings) as g:
        w.set_block((1,2,3),BLOCK_ID_BY_NAME["GRASS"])
