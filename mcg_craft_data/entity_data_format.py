# chunks are in chunk_block_files and are loaded with mmap (write through)
# block entity data (and all other entities) are in chunk_entity_files and loaded with literal_eval into the game
# metadata file in folder that contains stuff like which number is which item -> {1:"mcgcraft:stone",2:"mcgcraft:grass",...}
# block entity files are autosaved in regular intervalls and on exit of the game
# use bigger chunks for better efficiency (64)

world = {
    "chunksize":64,
    "worldgenerator":"colorland",
    "entities" : {"someentity":[0,0,0],"Joram":[0,0,0]},
    # from seperate files:
    "chunks" : {
        (0,0,0) : {
            "block_file" : "bytearray, byte per block depend on number of different blocks inside of this chunk (normally 1)", #loaded with mmap
            "nbt_file" : { #loaded with literal eval
                "entities" : {
                    "someentity" : {
                        "id":"mcgcraft:sheep",
                        "position":(0,0,0),
                        "movement":(0,0,0),
                        },
                    "Joram" : {
                        "id":"mcgcraft:player",
                        "position":(0,0,0),
                        "movement":(0,0,0),
                        "password":"schlumpf",
                        "mining":0, #ticks since started mining or last broken block
                        "inventory":[],
                        },
                    },
                "block_entity_data" : {
                    (0,0,0) : {"inventory":[{"id":"mcgcraft:sword","count":4,"slot":5}]}
                    },
                "metadata" : {
                    "byte_per_block":1,
                    "block_codec" : ["mcgcraft:stone","mcgcraft:grass","..."],
                    },
                },
            },
        },
    # runtime
    "active chunks" : [(0,0,0)],
    }


class World(object):
    def __init__(self,path):
        pass
    def get_block(self,position):
        pass
    def set_block(self,position):
        pass
    def get_entity_data(name):
        pass
    def set_entity_data(name,value):
        pass

class TrappedList(list):
    pass

class TrappedDict(dict):
    pass

class Entity(dict):
    SPEED = 5
    def __init__(self,world,*args,**kwargs):
        self.world = world
        self.observers = set()
        self.callbacks = {}

        self.register_callback("position",self._on_position_change) #still to handle: world change
        self.register_callback("rotation",self._notify_chunk_observers)
        self.register_callback("texture", self._notify_chunk_observers)

        dict.__init__(self,*args,**kwargs)
        self.setdefault("position",None)
        self.setdefault("rotation",(0,0))
        self.setdefault("texture",0)

    def register_callback(self,key,callback):
        """callback(previous_value, new_value) will be called each time value of key got changed"""
        callbacklist = self.callbacks.setdefault(key,[])
        callbacklist.append(callback)

    def __setitem__(self,key,new_value):
        previous_value = self[key]
        dict.__setitem__(self,key,new_value)
        for callback in self.callbacks.get(key,[]):
            callback(previous_value,new_value)

    def _on_position_change(self, old_position, new_position):
        """set position of entity"""
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

    def _notify_chunk_observers(self,*_):
        if self.world:
            for observer in self.world._get_chunk(self["position"]).observers:
                observer._set_entity(self)

"""Player has to register on it's own
        # observer of this entity (the player)
        for observer in self.observers:
            observer._notice_position(position, world)
"""
