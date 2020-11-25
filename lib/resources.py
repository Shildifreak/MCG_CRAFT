import sys, os, inspect, imp
import math, random, time, collections
import tempfile

PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

from TPManager.tp_compiler import TP_Compiler

import voxelengine
from voxelengine.modules.shared import *
from voxelengine.modules.utils import operator_friendly_set
from voxelengine.modules.geometry import Vector, Hitbox, BinaryBox, Sphere, Point, Box
from voxelengine.server.event_system import Event

GRAVITY = 35
AIRSLIDING = 1
SLIDING = 0.000001


class Block(voxelengine.Block):
    blast_resistance = 0
    defaults = {"p_level":0, # redstone power level
                "p_stronglevel":None, # only used on solid blocks so solid blocks powered by redstone don't power other redstone
                "p_ambient":False, # power nonsolid blocks in all directions
                "p_directions":(), # power solid blocks in these directions
                "rotation":0,"base":"b"}

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
        if key == "id":
            self.morph()
        if value == self.defaults.get(key,(value,)): #(value,) is always != value, so if there is no default this defaults to false
            super(Block,self).__delitem__(key)
        else:
            super(Block,self).__setitem__(key,value)

    def handle_event_default(self, events):
        print("No handler for event",events[0].tag)
    
    def handle_events(self, events):
        """API for event system"""
        grouped_events = collections.defaultdict(set)
        for event in events:
            grouped_events[event.tag].add(event)
        for tag, events in grouped_events.items():
            f_name = "handle_event_"+tag
            f = getattr(self, f_name, self.handle_event_default)
            f(events)

    # helper functions
    def redstone_activated(self):
        for face in FACES:
            nachbarblock = self.relative[face]
            if nachbarblock["p_level"]:
                if nachbarblock["p_ambient"] or -face in nachbarblock["p_directions"]:
                    return True
        return False

    def block_to_world_vector(self, vector):
        def r_x(v):
            x, y, z = v
            return Vector((  x, -z,  y)) #maybe need to swap sign on z,y
            
        def r_y(v):
            x, y, z = v
            return Vector((  z,  y, -x))

        c = {1:3,2:2,3:1,0:0}[self["rotation"]]
        for _ in range(c):
            vector = r_y(vector)
        #  e
        #n   s
        #  w
        base = self["base"]
        if base == "t":
            return r_x(r_x(vector))
        if base == "n":
            c = 0
        elif base == "e":
            c = 3
        elif base == "s":
            c = 2
        elif base == "w":
            c = 1
        else:
            return vector
        vector = r_x(vector)
        for _ in range(c):
            vector = r_y(vector)
        return vector
            
    
    def get_base_vector(self):
        return self.block_to_world_vector(Vector((0,-1,0)))
        #return {"t":Vector(( 0, 1, 0)),
        #        "b":Vector(( 0,-1, 0)),
        #        "s":Vector(( 0, 0, 1)),
        #        "n":Vector(( 0, 0,-1)),
        #        "e":Vector(( 1, 0, 0)),
        #        "w":Vector((-1, 0, 0)),
        #       }[self["base"]]

    def get_front_facing_vector(self):
        return self.block_to_world_vector(Vector((0,0,-1)))

    def get_right_facing_vector(self):
        return self.block_to_world_vector(Vector((1,0,0)))
        
    def get_bounding_box(self):
        return BinaryBox(0, self.position).bounding_box()
    
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
        block = self.blockworld[self.position]
        character.pickup_item({"id":self["id"],"count":1})
        self.blockworld[self.position] = "AIR"
        

    def handle_event_explosion(self,events):
        for event in events: #M# could add up power of events or something
            #if isinstance(event.area, Sphere):
            #    position, power = event.area.center, event.area.radius
            #    distance = (position - self.position).length()
            if random.random() > self.blast_resistance:
                self.world.blocks[self.position] = "AIR"

    def get_tags(self):
        """
        return tags of this entity, this can be events that it reacts to or just for finding it in the world
        default tags include:
        - solid     .. which means they got a hitbox (see collides_with for further instruction
        - explosion .. this block got an event handler for explosions
        """
        return operator_friendly_set({"solid", "explosion"})

    def collides_with(self, area):
        """
        if a block is solid and his bounding box collides with <area>,
        this method is used to test if they actually collide
        """
        return True #full blocks always collide if their bounding box collides

class SolidBlock(Block):
    defaults = Block.defaults.copy()
    defaults["p_stronglevel"] = 0
    defaults["p_ambient"] = True
    def handle_event_block_update(self,event):
        """directions indicates where update(s) came from... usefull for observer etc."""
        """for pure cellular automata action make sure to not set any blocks but only return new state for this block (use schedule to do stuff that effects other blocks)"""
        # redstone Zeug
        level = 0
        stronglevel = 0
        for face in FACES:
            neighbour = self.relative[-face]
            if (face in neighbour["p_directions"]):
                level = max(level, neighbour["p_level"])
                if neighbour != "Redstone":
                    stronglevel = max(stronglevel, neighbour["p_level"])
        self["p_level"] = level
        self["p_stronglevel"] = stronglevel
        self.save()

    def get_tags(self):
        return super(SolidBlock, self).get_tags().union({"block_update"})

# Default Item and Block (also usefull for inheritance)

class Item(object):
    # Init function, don't care too much about this
    def __init__(self,item):
        self.item = item
        self.tags = item.setdefault("tags",{})
        self.item.setdefault("count",1)

    # FUNCTIONS TO BE OVERWRITTEN IN SUBCLASSES:
    def block_version(self):
        """use the output of this function when trying to place the item into the world as a block"""
        return self.item["id"]
    
    def block_version_on_place(self, character, blockpos, face):
        return self.block_version()
    
    def use_on_block(self,character,blockpos,face):
        """whatever this item should do when click on a block... default is to place a block with same id"""
        new_pos = blockpos + face

        # check if block would collide with player
        blockdata = self.block_version_on_place(character,blockpos,face)
        block = Block(blockdata, position=new_pos, blockworld=character.world.blocks)
        if "solid" in block.get_tags():
            for entity in character.world.entities.find_entities(block.get_bounding_box()):
                if block.collides_with( entity.HITBOX + entity["position"] ):
                    return

        # place block in world and decrease item count
        block.save()
        self.item["count"] -= 1
        if self.item["count"] <= 0:
            parent_key = self.item.parent.index(self.item)
            self.item.parent[parent_key] = {"id": "AIR"}
            

    def use_on_entity(self,character,entity):
        """
        whatever this item should do when clicked on this entity... default is to do the same like when clicking air
        Return value signalizes whether to also execute right_/left_clicked action of entity
        """
        return self.use_on_air(character)

    def use_on_air(self,character):
        """whatever this item should do when clicked into air"""
        return True

class Entity(voxelengine.Entity):
    HITBOX = Hitbox(0,0,0)
    LIMIT = 0
    instances = []

    def __init__(self,*args,**kwargs):
        super(Entity,self).__init__(*args,**kwargs)

        self["velocity"] = Vector([0,0,0])
        self["last_update"] = time.time()
        self["ACCELERATION"] = 20
        self["SPEED"] = 10
        
        self.register_item_sanitizer(lambda v: Vector(v),"velocity")

        self.instances.append(self)

    def kill(self):
        self.instances.remove(self)
        self.set_world(None, Vector((0,0,0)))
    
    def right_clicked(self, character):
        """whatever this entity should do when being right clicked by entity"""

        r = character.get_sight_vector()
        self["velocity"] = Vector(r)*(20,0,20) + Vector((0,15,0))

    def left_clicked(self, character):
        """whatever this entity should do when being right clicked by entity"""

        a = character["lives"]

        if a<20:

            b = character["lives"] + 1

            character["lives"] = b

    
    @classmethod
    def try_to_spawn(cls, world):
        x = random.randint(-40,40)
        y = random.randint(-10,20)
        z = random.randint(-40,40)
        block = world.blocks[(x,y-3,z)]
        area = cls.HITBOX+Vector(x,y,z)
        if block != "AIR" and not any(True for _ in world.blocks.find_blocks(area, "solid")):
            print("spawning",cls,"at position",(x,y,z))
            entity = cls()
            entity.set_world(world,(x,y,z))
            return entity
    
    def onground(entity):
        return entity.bool_collide_difference(entity["position"]+(0,-0.2,0),entity["position"])

    def collide_blocks(entity):
        """blocks entity collides with"""
        return entity.potential_collide_blocks(entity["position"])

    def potential_collide_blocks(entity,position):
        """blocks entity would collide with if it was at position"""
        area = entity.HITBOX+position
        blocks = entity.world.blocks.find_blocks(area, "solid")
        return (block for block in blocks if block.collides_with(area))

    def collide_difference(entity,new_position,previous_position):
        """return blocks entity would newly collide with if it moved from previous_position to new_position"""
        #M# maybe create area that is difference of previous hitbox and new hitbox and use that for finding blocks in world, but that has to be supported by collision forms first
        if False:
            diff_area = DiffArea(entity.HITBOX+new_position, entity.HITBOX+previous_position)
            blocks = entity.world.blocks.find_blocks(diff_area, "solid")
            return (block for block in blocks if block.collides_with(diff_area))
        blocks = entity.potential_collide_blocks(new_position)
        prev_area = entity.HITBOX+previous_position
        return (block for block in blocks if not (BinaryBox(0, block.position).bounding_box().collides_with(prev_area) and
                                                  block.collides_with(prev_area)))

    def bool_collide_difference(entity,new_position,previous_position):
        #M# can be optimized because only one hit is needed, but it still has to pass the blocks colides_with test, so make sure find_blocks is a generator
        return any(True for _ in entity.collide_difference(new_position, previous_position))
    
    def horizontal_move(entity,jump): #M# name is misleading
        if entity.onground():
            s = SLIDING**entity.dt
            ev = entity["velocity"]
            if ev[1] < 0:
                ev *= (1,0,1)
            if jump:
                ev = (ev[0], max(ev[1],entity["JUMPSPEED"]),ev[2])
            entity["velocity"] = ev
        else:
            s = AIRSLIDING**entity.dt
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
        #M# todo: cast ray from each point to detect collision and so on !!!
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

    def pickup_item(self,item):
        a = False
        i_air = None
        for i,inv_item in enumerate(self["inventory"]):
            if i_air == None and inv_item["id"] == "AIR":
                i_air = i
            if inv_item["id"] == item["id"]:
                inv_item["count"] = inv_item.get("count", 1) + item["count"]
                return True
        if i_air == None:
            return False
        self["inventory"][i_air] = item
        return True

blockClasses    = None # initialized in load_resources_from
itemClasses     = None # initialized in load_resources_from
entityClasses   = None # initialized in load_resources_from

def register_item(name):
    def _register_item(item_subclass):
        if name in itemClasses:
            print("Warning: %s replaces previous definition %s" % (item_subclass, itemClasses[name]))
        itemClasses[name] = item_subclass
        return item_subclass
    return _register_item

def register_block(name):
    def _register_block(block_subclass):
        if name in blockClasses:
            print("Warning: %s replaces previous definition %s" % (block_subclass, blockClasses[name]))
        blockClasses[name] = block_subclass
        return block_subclass
    return _register_block

def register_entity(name):
    def _register_entity(entity_subclass):
        if name in entityClasses:
            print("Warning: %s replaces previous definition %s" % (entity_subclass, entityClasses[name]))
        entityClasses[name] = entity_subclass
        return entity_subclass
    return _register_entity

texturepackDirectory = tempfile.TemporaryDirectory()
texturepackPath = texturepackDirectory.name

def load_resources_from(resource_paths):
    global blockClasses, itemClasses, entityClasses

    blockClasses  = collections.defaultdict(lambda:SolidBlock)
    itemClasses   = collections.defaultdict(lambda:Item)
    entityClasses = collections.defaultdict(lambda:Entity)
        
    for resource_path in resource_paths:
        structure_path = os.path.join(PATH, "..", "resources", resource_path, "structures")
        sys.path.append(structure_path)
        for directory in ("blocks","entities"):
            path = os.path.join(PATH, ".." , "resources", resource_path, directory) #everything before resource_path is dropped in case of absolute path
            if os.path.isdir(path):
                for fn in os.listdir(path):
                    if fn.endswith(".py") and not fn.startswith("_"):
                        imp.load_source(fn[:-3],os.path.join(path,fn)) #like adding to path and removing afterwards, but shorter (also it's deprecated in 3.3)
        sys.path.remove(structure_path)

    tp_compiler = TP_Compiler()
    for resource_path in resource_paths:
        textures_path = os.path.join(PATH, "..", "resources", resource_path, "textures")
        if os.path.isdir(textures_path):
            print(textures_path)
            tp_compiler.add_textures_from(textures_path)
    tp_compiler.save_to(texturepackPath)
