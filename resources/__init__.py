import sys, os, inspect, imp
import math, random, time, collections

PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

import voxelengine
from shared import *

GRAVITY = 35
AIRRESISTANCE = 5
SLIDING = 0.001


class Block(voxelengine.Block):
    defer = False
    deferred = [] #Block, key, value
    
    blast_resistance = 0
    defaults = {"p_level":0,
                "p_stronglevel":None,
                "p_ambient":True,
                "p_directions":(),}#"rotation":0,"base":"b"}

    def __init__(self,*args,**kwargs):
        super(Block,self).__init__(*args,**kwargs)
        self.morph()
    
    def morph(self):
        self.__class__ = blockClasses[self["id"]]

    def __getitem__(self, key):
        try:
            return super(Block, self).__getitem__(key)
        except KeyError:
            return self.defaults.get(key,None)
    def __setitem__(self, key, value):
        if value == self[key]:
            return
        if Block.defer:
            Block.deferred.append((self,key,value))
            return
        if key == "id":
            self.morph()
        if value == self.defaults.get(key,(value,)): #(value,) is always != value, so if there is no default this defaults to false
            super(Block,self).__delitem__(key)
        else:
            super(Block,self).__setitem__(key,value)
        self.world.changed_blocks.append(self.position)
        
    # FUNCTIONS TO BE OVERWRITTEN IN SUBCLASSES:
    def block_update(self,directions):
        """directions indicates where update(s) came from... usefull for observer etc."""
        """for pure cellular automata action make sure to not set any blocks but only return new state for this block (use schedule to do stuff that effects other blocks)"""

    def random_ticked(self):
        """spread grass etc"""

    def activated(self,character,face):
        """blocks like levers should implement this action. Return value signalizes whether to execute use action of hold item"""
        return True

    def mined(self,character,face):
        """drop item or something... also remember to set it to air. Return value see activated"""
        block = self.world[self.position]
        character["right_hand"] = {"id":block["id"]}
        self.world[self.position] = "AIR"

    def exploded(self,entf):
        if entf < 1:
            if random.random() > self.blast_resistance:
                self.world[self.position] = "AIR"

    def collides_with(self,hitbox,position):
        #print type(self), self.__class__, self["id"], blockClasses[self["id"]]
        return True

class SolidBlock(Block):
    defaults = Block.defaults.copy()
    defaults["p_stronglevel"] = 0
    def block_update(self,directions):
        """directions indicates where update(s) came from... usefull for observer etc."""
        """for pure cellular automata action make sure to not set any blocks but only return new state for this block (use schedule to do stuff that effects other blocks)"""
        # redstone Zeug
        level = 0
        stronglevel = 0
        for face in FACES:
            neighbour = self.world[self.position-face]
            if (face in neighbour["p_directions"]):
                level = max(level, neighbour["p_level"])
                if neighbour != "Redstone":
                    stronglevel = max(stronglevel, neighbour["p_level"])
        self["p_level"] = level
        self["p_stronglevel"] = stronglevel
        #M# return instead of inplace variation

# Default Item and Block (also usefull for inheritance)

class Item(object):
    # Init function, don't care to much about this
    def __init__(self,item):
        self.item = item
        self.tags = item.setdefault("tags",{})

    # FUNCTIONS TO BE OVERWRITTEN IN SUBCLASSES:
    def use_on_block(self,character,blockpos,face):
        """whatever this item should do when click on a block... default is to place a block with same id"""
        new_pos = blockpos + face
        block_id = self.item["id"]
        character.world[new_pos] = block_id
        #M# remove block again if it collides with placer (check for all entities here later)
        if new_pos in character.collide(character["position"]):
            character.world[new_pos] = "AIR"        

    def use_on_entity(self,character,entity):
        """whatever this item should do when clicked on this entity... default is to do the same like when clicking air"""
        self.use_on_air(character)

    def use_on_air(self,character):
        """whatever this item should do when clicked into air"""


def floatrange(a,b):
    return [i+a for i in range(0, int(math.ceil(b-a))) + [b-a]]

def get_hitbox(width,height,eye_level):
    return [(dx,dy,dz) for dx in floatrange(-width,width)
                       for dy in floatrange(-eye_level,height-eye_level)
                       for dz in floatrange(-width,width)]

class Entity(voxelengine.Entity):
    HITBOX = ()
    LIMIT = 0
    instances = []

    def __init__(self,*args,**kwargs):
        super(Entity,self).__init__(*args,**kwargs)
        self.instances.append(self)
    
    @classmethod
    def try_to_spawn(cls, world):
        x = random.randint(-40,40)
        z = random.randint(-10,10)
        y = random.randint(-40,40)
        block = world.get_block((x,y-2,z),load_on_miss = False)
        if block and block != "AIR" and len(cls.class_collide(world,Vector((x,y,z)))) == 0:
            entity = cls(world)
            entity.set_world(world,(x,y,z))

    @classmethod
    def class_collide(cls, world, position):
        blocks = set()
        for relpos in cls.HITBOX:
            block_pos = (position+relpos).normalize()
            if world.get_block(block_pos).collides_with(cls.HITBOX,position):
                blocks.add(block_pos)
        return blocks
    
    def onground(entity):
        return entity.bool_collide_difference(entity["position"]+(0,-0.2,0),entity["position"])

    def collide(entity,position):
        """blocks entity would collide with if it was at position"""
        return entity.class_collide(entity.world,position)

    def potential_collide_blocks(entity,position):
        blocks = set()
        for relpos in entity.HITBOX:
            block_pos = (position+relpos).normalize()
            blocks.add(block_pos)
        return blocks

    def collide_difference(entity,new_position,previous_position):
        """return blocks entity would newly collide with if it moved from previous_position to new_position"""
        return collide(entity,new_position).difference(collide(entity,previous_position))

    def bool_collide_difference(entity,new_position,previous_position):
        for block in entity.potential_collide_blocks(new_position).difference(entity.potential_collide_blocks(previous_position)):
            if entity.world.get_block(block).collides_with(entity.HITBOX,entity["position"]):
                return True
        return False
    
    def horizontal_move(entity,jump): #M# name is misleading
        if entity.onground():
            s = 0.5*SLIDING**entity.dt
            entity["velocity"] *= (1,0,1) #M# stop falling
            if jump:
                entity["velocity"] += (0,entity["JUMPSPEED"],0)
        else:
            s = 0.5*AIRRESISTANCE**entity.dt
            entity["velocity"] -= Vector([0,1,0])*GRAVITY*entity.dt
        sv = Vector([s,1,s]) #no slowing down in y
        entity["velocity"] *= sv
        return sv

    def update(self):
        pass

    def update_dt(entity):
        entity.dt = time.time()-entity["last_update"]
        entity.dt = min(entity.dt,1) # min slows time down for players if server is pretty slow
        entity["last_update"] = time.time()

    def update_position(entity):
        steps = int(math.ceil(max(map(abs,entity["velocity"]*entity.dt))*10)) # 10 steps per block
        pos = entity["position"]
        for step in range(steps):
            for i in range(DIMENSION):
                mask          = Vector([int(i==j) for j in range(DIMENSION)])
                inverted_mask = Vector([int(i!=j) for j in range(DIMENSION)])
                new = pos + entity["velocity"]*entity.dt*mask*(1.0/steps)
                if entity.bool_collide_difference(new,pos):
                    entity["velocity"] *= inverted_mask
                else:
                    pos = new
        if pos != entity["position"]:
            entity["position"] = pos
    
    def block_update(self):
        """called when block "near" entity is changed"""
        pass

blockClasses  = collections.defaultdict(lambda:SolidBlock)
itemClasses   = collections.defaultdict(lambda:Item)
entityClasses = collections.defaultdict(lambda:Entity)

def register_item(name):
    def _register_item(item_subclass):
        itemClasses[name] = item_subclass
        return item_subclass
    return _register_item

def register_block(name):
    def _register_block(block_subclass):
        blockClasses[name] = block_subclass
        return block_subclass
    return _register_block

def register_entity(name):
    def _register_entity(entity_subclass):
        entityClasses[name] = entity_subclass
        return entity_subclass
    return _register_entity

for directory in ("blocks","entities"):
    path = os.path.join(PATH,directory)
    for fn in os.listdir(path):
        if fn.endswith(".py") and not fn.startswith("_"):
            imp.load_source(fn[:-3],os.path.join(path,fn)) #like adding to path and removing afterwards, but shorter (also it's deprecated in 3.3)
