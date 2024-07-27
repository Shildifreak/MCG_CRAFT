import sys, os, inspect
import math, random, time, collections, itertools
import tempfile
import warnings

# deprecated
#from imp import load_source

# importlib (has problems with feature modules importing each other, causing false positive shadow warnings, something about path vs meta_path)
#import importlib.util
#def load_source(module_name, module_path):
#    spec = importlib.util.spec_from_file_location(module_name, module_path)
#    module = importlib.util.module_from_spec(spec)
#    spec.loader.exec_module(module)

# workaround/solution using path manipulation and standart import mechanism
def load_source(module_name, module_path):
    sys.path.insert(0, os.path.dirname(module_path))
    __import__(module_name)
    sys.path.pop(0)

PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

from TPManager.tp_compiler import TP_Compiler

import voxelengine
from voxelengine.modules.shared import *
from voxelengine.modules.geometry import Vector, Hitbox, BinaryBox, Sphere, Point, Box, avg360, NOWHERE
from voxelengine.modules.observableCollections import observable_from, Observable
from voxelengine.modules.serializableCollections import Serializable, serialize, extended_literal_eval
from voxelengine.modules.utils import SubclassTracker
from voxelengine.server.event_system import Event

GRAVITY = 35
WATER_GRAVITY = -10
AIRSLIDING = 1
SLIDING = 0.000001
WATERSLIDING = 0.2

class PowerLevelAccumulator(object):
    __slots__ = ("level", "abs_level")
    def __init__(self):
        self.level = 0
        self.abs_level = 0
    def add(self, level):
        abs_level = abs(level)
        if abs_level >= self.abs_level:
            if abs_level == self.abs_level and level != self.level: #same power but different sign
                self.level = 0
            else:
                self.level = level
            self.abs_level = abs_level

def wait(dt):
    """a wait for asynchronous action handlers for onclick etc."""
    t0 = time.time()
    while time.time() - t0 < dt:
        yield

class Block(voxelengine.Block, metaclass=SubclassTracker):
    blast_resistance = 0
    defaults = {"p_level":0, # redstone power level
                "p_stronglevel":None, # only used on solid blocks so solid blocks powered by redstone don't power other redstone
                "p_ambient":False, # power nonsolid blocks in all directions
                "p_directions":(), # power solid blocks in these directions
                "rotation":0,"base":"b"}

    def __init__(self, data, *args,**kwargs):
        default_data = self.defaults.copy()
        default_data.update(data)
        super().__init__(default_data, *args, **kwargs)
        
        assert type(self) != Block #this is an abstract class, please instantiate specific subclasses or use BlockFactory
        assert Block.subclasses[self["id"]] == type(self) #blocks must have a matching type id
    
    def turn_into(self, new_block):
        self.clear()
        if isinstance(new_block, str):
            super().__setitem__("id", new_block)
        else:
            self.update(new_block)
        self._morph()
    
    def _morph(self):
        self.__class__ = Block.subclasses[self["id"]]

    def __getitem__(self, key):
        return self.get(key,None)

    def __setitem__(self, key, value):
        if value == self[key]:
            return
        super().__setitem__(key,value)
        if key == "id":
            self._morph()

    def handle_event_default(self, events):
        tag = events.pop().tag
        # only print message if the block still has the tag, because if the block just
        # changed in this subtick it may still receive events that don't effect it anymore
        if tag in self.get_tags():
            print("No handler for event", event.tag)
        return False
    
    def handle_events(self, events):
        """API for event system"""
        any_changed = False
        grouped_events = collections.defaultdict(set)
        for event in events:
            grouped_events[event.tag].add(event)
        for tag, events in grouped_events.items():
            f_name = "handle_event_"+tag
            f = getattr(self, f_name, self.handle_event_default)
            changed = f(events)
            if __debug__:
                if not isinstance(changed, bool):
                    raise ValueError("event handler function %s has to return a bool representing whether it changed the block" % f)
            any_changed = any_changed or changed
        return any_changed

    # helper functions
    def ambient_power_level(self):
        ambient_power = PowerLevelAccumulator()
        for face in FACES:
            neighbour = self.relative[-face]
            if neighbour["p_ambient"] or (face in neighbour["p_directions"]):
                ambient_power.add(neighbour["p_level"])
        return ambient_power.level
    
    def power_levels(self):
        power = PowerLevelAccumulator()
        strong_power = PowerLevelAccumulator()
        for face in FACES:
            neighbour = self.relative[-face]
            if face in neighbour["p_directions"]:
                power.add(neighbour["p_level"])
                if neighbour != "Redstone":
                    strong_power.add(neighbour["p_level"])
        return power.level, strong_power.level
    
    def redstone_activated(self):
        return self.ambient_power_level() > 0

    def bluestone_activated(self):
        return self.ambient_power_level() < 0

    def block_to_world_vector(self, vector):
        def r_x(v):
            x, y, z = v
            return Vector((  x, -z,  y))
            
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

    def clicked(self,character,face,item):
        """blocks like levers should implement this action. Return value signalizes whether to execute use action of hold item"""
        return item.use_on_block(character, self, face)

    def item_version(self):
        """use the output of this function when turning the block into an item"""
        return {"id":self["id"],"count":1}

    def mined(self,character,face):
        """drop item or something... also remember to set it to air. Return value see activated"""
        character.pickup_item(self.item_version())
        self.blockworld[self.position] = "AIR"
        sound_event = Event("sound",Point(self.position),self.get_break_sound())
        self.world.event_system.add_event(sound_event)

    def handle_event_explosion(self,events):
        """default implementation for handling explosion events"""
        for event in events: #M# could add up power of events or something
            #if isinstance(event.area, Sphere):
            #    position, power = event.area.center, event.area.radius
            #    distance = (position - self.position).length()
            if random.random() > self.blast_resistance:
                self.turn_into("AIR")
                return True
        return False

    def get_break_sound(self):
        return self["id"]+"_block_broken"

    def get_place_sound(self):
        return self["id"]+"_block_placed"

    def get_tags(self):
        """
        return tags of this entity, this can be events that it reacts to or just for finding it in the world
        default tags include:
        - solid     .. which means they got a hitbox (see collides_with for further instruction
        - explosion .. this block got an event handler for explosions
        """
        return {"solid", "explosion"}

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
        prev_levels = self["p_level"], self["p_stronglevel"]
        p_levels = self.power_levels()
        if p_levels != prev_levels:
            self["p_level"], self["p_stronglevel"] = p_levels
            return True
        return True

    def get_tags(self):
        return super(SolidBlock, self).get_tags().union({"block_update"})

class Item(object, metaclass=SubclassTracker):
    # Init function, don't care too much about this
    def __init__(self,item):
        if isinstance(item, Item):
            self.item = item.item
            return
        self.item = item
        #self.tags = item.setdefault("tags",{})
        self.item.setdefault("count",1)

        assert Item.subclasses[self.item["id"]] == type(self) #item class must match id

    # FUNCTIONS TO BE OVERWRITTEN IN SUBCLASSES:
    def block_version(self):
        """use the output of this function when trying to place the item into the world as a block"""
        return self.item["id"]
    
    def block_version_on_place(self, character, block, face):
        return self.block_version()

    def entity_blockmodel(self):
        return self.item["id"]
    
    max_distance = 5
    interval = 0.1
    def use_on_block(self,character,block,face):
        """whatever this item should do when click on a block... default is to place a block with same id"""
        self.place(character,block,face)

        # if button is still held down after a short delay, continue by placing more blocks
        yield from wait(0.2)
        while True:
            pressure = yield
            distance, pos, face = character.get_focused_pos(self.max_distance)
            if pos:
                block = character.world.blocks[pos]
                self.place(character, block, face)
                if self.item["count"] <= 0: #stop placing if stack is empty
                    return
                yield from wait(self.interval)

    def place(self, character, block, face):
        new_pos = block.position + face

        # check if block would collide with player
        blockdata = self.block_version_on_place(character,block,face)
        block = BlockFactory(blockdata, position=new_pos, blockworld=character.world.blocks)
        if "solid" in block.get_tags():
            for entity in character.world.entities.find_entities(block.get_bounding_box()):
                if block.collides_with( entity.HITBOX + entity["position"] ):
                    return

        # place block in world and decrease item count
        if self.decrease_count():
            block.save()
            
            # play sound
            sound_event = Event("sound",Point(block.position),block.get_place_sound())
            block.world.event_system.add_event(sound_event)
        return
    
    def decrease_count(self):
        """
        tries to decrease the count of this item by 1
        returns whether that was successful
        """
        if self.item["count"] <= 0:
            return False
        self.item["count"] -= 1
        if self.item["count"] == 0:
            parent_key = self.item.parent_key
            if parent_key == None:
                parent_key = self.item.parent.index(self.item)
            self.item.parent.replace(parent_key, {"id": "AIR"})
        return True
            

    def use_on_entity(self,character,entity):
        """
        whatever this item should do when clicked on entity
        use yield or return a generator to continue action as long as key is hold
        return bool to signalize whether to also execute clicked action of entity
        """
        return entity.clicked(character, self)

    def use_on_air(self,character):
        """whatever this item should do when clicked into air"""
        return True

class UnplacableItem(Item):
    def use_on_block(self,character,blockpos,face):
        """whatever this item should do when click on a block... default is to place a block with same id"""
        return self.use_on_air(character)

class ItemData(dict):
    pass

def InventoryFactory(inventory):
    if not isinstance(inventory, Observable):
        inventory = observable_from(inventory)
    inventory.register_default_item_sanitizer(ItemData)
    return inventory

class SubclassTracker_Entity(SubclassTracker, type(voxelengine.Entity)): #observable inherits from abc with uses abc.ABCMeta metaclass
    pass

class Entity(voxelengine.Entity, metaclass=SubclassTracker_Entity):
    HITBOX = Hitbox(0.25,0.5,0.25)
    LIMIT = 0
    PASSENGER_OFFSETS = (Vector(0,1.5,0),)
    instances = []

    def __init__(self, data = None):
        data_defaults = {
            "velocity" : Vector([0,0,0]),
            "flying" : False,
            "health" : 10,
            "max_health" : 10,
            "ACCELERATION" : 20,
            "SPEED" : 10,
        }
        if data != None:
            data_defaults.update(data)
        super().__init__(data_defaults)
        
        assert Entity.subclasses[self["type"]] == type(self) #entities must have a matching type item
        
        self.register_item_sanitizer(Vector,"velocity")
        self.register_item_sanitizer(InventoryFactory, "inventory")
        self.register_item_sanitizer(lambda h: min(h, self["max_health"]), "health")
        self.register_item_callback(self._check_health,"health")

        self.ai_commands = collections.defaultdict(list)

        self.riding = None # entity or None
        self.passengers = [] # list of entities

        self.instances.append(self)

    def get_focused_pos(self, max_distance):
        blocktest = lambda block, ray: block.collides_with(ray)
        return super().get_focused_pos(max_distance, blocktest)

    def ride(self, entity):
        """attempt to ride entity
        return success"""
        if len(entity.passengers) >= len(entity.PASSENGER_OFFSETS):
            return False
        self.unmount_riding()
        self.riding = entity
        entity.passengers.append(self)
        return True

    def unmount_riding(self):
        if self.riding:
            self["velocity"] = self.riding["velocity"] #instead of potentially large velocity from trying to reach vehicle
            self.riding.passengers.remove(self)
            self.riding = None

    def unmount_passengers(self):
        for p in self.passengers:
            p.riding = None
        self.passengers = []

    def unmount_all(self):
        self.unmount_riding()
        self.unmount_passengers()
    
    def check_mounts(self):
        if self.riding:
            if self not in self.riding.passengers:
                self.riding = None
        for p in self.passengers[:]:
            if p.riding != self:
                self.passengers.remove(p)

    def kill(self):
        self.unmount_all()
        if self in self.instances:
            self.instances.remove(self)
            self.set_world(None, Vector((0,0,0)))
        elif __debug__:
            print("this entity is already dead")
    
    def _check_health(self, health):
        if health < 0:
            self.kill()
    
    def handle_event_default(self, events):
        tag = events.pop().tag
        print("No handler for event", event.tag)

    def handle_events(self, events):
        """API for event system"""
        grouped_events = collections.defaultdict(set)
        for event in events:
            grouped_events[event.tag].add(event)
        for tag, events in grouped_events.items():
            f_name = "handle_event_"+tag
            f = getattr(self, f_name, self.handle_event_default)
            f(events)
    
    def clicked(self, character, item):
        """whatever this entity should do when being clicked by character with item"""
        pass
    
    @classmethod
    def test_spawn_conditions(cls, world, position):
        block = world.blocks[position - (0,3,0)]
        area = cls.HITBOX + position
        return (block != "AIR" and not any(True for _ in world.blocks.find_blocks(area, "solid")))
    
    def onground(entity,vel_pos_pair=None):
        if vel_pos_pair == None:
            position = entity["position"]
            velocity = entity["velocity"]
        else:
            velocity, position = vel_pos_pair
        if velocity[1] > 0:
            return False
        return entity.bool_collide_difference(position+(0,-0.2,0),position)

    def inwater(entity):
        position = entity["position"]
        area = entity.HITBOX+position
        b = next(entity.world.blocks.find_blocks(area, "water"),None)
        return bool(b)

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
    
    def horizontal_move(entity,jump=False,shift=False): #M# name is misleading
        inwater = entity.inwater()
        if entity.onground() and not inwater:
            s = SLIDING**entity.dt
            sy = 1
            ev = entity["velocity"]
            #if ev[1] < 0:
            #    ev *= (1,0,1)
            if jump:
                ev = (ev[0], max(ev[1],entity["JUMPSPEED"]),ev[2])
            entity["velocity"] = ev
        else:
            if inwater:
                g = WATER_GRAVITY
                if jump:
                    ev = entity["velocity"]
                    entity["velocity"] = (ev[0], max(ev[1],entity["JUMPSPEED"]),ev[2])
                elif shift:
                    g = - WATER_GRAVITY
                sy = WATERSLIDING**entity.dt
            else:
                g = GRAVITY
                sy = 1
            s = AIRSLIDING**entity.dt
            entity["velocity"] -= Vector([0,1,0])*g*entity.dt
        sv = Vector([s,sy,s]) #no slowing down in y
        entity["velocity"] *= sv
        return sv

    apply_physics = horizontal_move

    def update(self):
        pass

    @property
    def dt(self):
        return self.world.clock.dt if self.world else 0

    def update_position(entity, sneak=False):
        """
        apply velocity to position
        call in update after update_dt
        """
        #M# todo: cast ray from each point to detect collision and so on !!!
        steps = int(math.ceil(max(map(abs,entity["velocity"]*entity.dt))*10)) # 10 steps per block
        pos = entity["position"]
        velocity = entity["velocity"]
        sneak = sneak and entity.onground() #can't sneak if not on ground to begin with
        for step in range(steps):
            for i in range(DIMENSION):
                mask          = Vector([int(i==j) for j in range(DIMENSION)])
                inverted_mask = Vector([int(i!=j) for j in range(DIMENSION)])
                new = pos + velocity*entity.dt*mask*(1.0/steps)
                if entity.bool_collide_difference(new,pos) or (sneak and not entity.onground((velocity,new))):
                    velocity *= inverted_mask
                else:
                    pos = new
        if pos != entity["position"]:
            entity["position"] = pos
        if velocity != entity["velocity"]:
            dv = (velocity - entity["velocity"]).length()
            entity["velocity"] = velocity
            # Geschwindigkeit 20 entspricht etwa einer Fallhoehe von 6 Block, also ab 7 nimmt der Spieler Schaden
            if dv > 1 and entity.riding:
                entity.unmount_riding()
                velocity = entity["velocity"]
                print("unmount by collision")
            if dv > 20:
                entity.take_damage(1)
    
    def execute_ai_commands(self):
        """
        call in update, automatically calls update_position
        """
        if self.riding:
            for command, values in self.ai_commands.items():
                self.riding.ai_commands[command].extend(values)

        jump   = bool(sum(self.ai_commands["jump"  ]))
        shift  = bool(sum(self.ai_commands["shift" ]))
        sprint = bool(sum(self.ai_commands["sprint"]))
        x = sum(self.ai_commands["x"])
        z = sum(self.ai_commands["z"])
        moveintent = bool(self.ai_commands["x"]) or bool(self.ai_commands["z"])

        yaw, pitch = self["rotation"]
        yaw_new, pitch_new = yaw, pitch
        if self.ai_commands["yaw"]:
            yaw_new = avg360(self.ai_commands["yaw"], yaw)
        if self.ai_commands["pitch"]:
            pitch_new = sum(self.ai_commands["pitch"]) / len(self.ai_commands["pitch"])
        if (yaw_new, pitch_new) != (yaw, pitch):
            self["rotation"] = (yaw_new, pitch_new)
        
        self.ai_commands.clear()


        if self.riding:
            if shift:
                self.unmount_riding()
                return

            i = self.riding.passengers.index(self)
            self["velocity"] = (self.riding["position"] + self.riding.PASSENGER_OFFSETS[i] - self["position"]) / self.dt
            self.update_position()
            return

        nv = Vector(x,0,z)
        speed_modifier = 2 if sprint else 1

        # Flying
        if self["flying"]:
            if jump:
                nv += (0, 1, 0)
            if shift:
                nv -= (0, 1, 0)
            if nv != (0,0,0):
                self["position"] += nv*self["FLYSPEED"]*speed_modifier*self.dt
            self["velocity"] = (0,0,0)
            return

        # Walking
        sv = self.horizontal_move(jump, shift)

        if moveintent:
            target_velocity = nv*self["SPEED"]*speed_modifier
            ax, _, az = target_velocity - self["velocity"]
            a_max = self["ACCELERATION"]
            ax = max(-a_max, min(a_max, ax))
            az = max(-a_max, min(a_max, az))
            
            self["velocity"] += (ax, 0, az)

        
        # update position
        sneak = shift and not self.inwater()
        self.update_position(sneak)

    def block_update(self):
        """called when block "near" entity is changed"""
        pass

    def take_damage(self, damage):
        self["health"] -= damage

    def find_inventory_slot(self, item={"id":"AIR"}):
        """return first inventory slot that contains matching item (ignoring count)"""
        for i,inv_item in enumerate(self["inventory"]):
            if inv_item["id"] == item["id"]:
                keys = set(inv_item.keys())-{"count"}
                if keys == set(item.keys())-{"count"}:
                    if all(inv_item[key] == item[key] for key in keys):
                        return i
        return None

    def pickup_item(self,item):
        """return success : bool"""
        if isinstance(item, Item):
            item = item.item
        # find a matching stack
        i = self.find_inventory_slot(item)
        if i != None:
            inv_item = self["inventory"][i]
            inv_item["count"] = inv_item.get("count", 1) + item.get("count",1)
            return True
        # or find an empty slot
        i = self.find_inventory_slot()
        if i != None:
            self["inventory"][i] = item
            return True
        # no space
        return False

class EntitySoul(object):
    """
    Souls control an entity by formulating an intend that is executed by the entity to the best of its ability.
    Entities may have multiple souls.
    Players are souls.
    Soul: Intend <-> Entity: Abilities
    """
    pass

class CommandException(Exception):
    pass

class Command(object):
    """
    permission_level:
          -1 - no commands allowed
        no effect
           0 - commands with no effects in game (whisper, help, log, ...)
        cosmetic
           1 - commands with cosmetic effect (skin, ...)
        negative to self
           2 - negative effects to originator (kill, damage, ...)
        insight
           3 - commands with slight insight (locate, ...)
        positive to self
           4.0 - commands with small positive effects (spawn, ...)
           4.1 - commands with medium positive effects (goto, ...)
           4.2 - commands with great positive effect (give, ...)
           4.9 - commands with creative power (gamemode, ...)
        directly affect world and other entities
           9 - commands that directly affect other entities (entity, setblock, ...)
        affect other players
          90 - commands that effect players (kick, ban, timeout, ...)
        permissions
         900 - commands that effect permissions (op, deop, ...)
        server
        9000 - server level commands (restart, stop, ...)
    """
    commands = {} # {name: command_func}

    @classmethod
    def register_command(cls, name, permission_level=9000):
        def _register_command(command):
            cls.commands[name] = command
            command.permission_level = permission_level
            return command
        return _register_command

    class COMMAND(object):
        @staticmethod
        def parse(self, context):
            command = Command.commands.get(self, None)
            if command == None:
                raise CommandException("unknown command name ",repr(self))
            return command

        @staticmethod
        def autocomplete(self, context):
            return [
                command_name + (" " if len(Command.get_arg_layout(command_func)) else "")
                for command_name, command_func in Command.commands.items()
                if context.permission_level >= command_func.permission_level \
                and command_name.startswith(self)
            ]

    @staticmethod
    def get_arg_layout(command_func):
        fas = inspect.getfullargspec(command_func)
        return [(a, fas.annotations[a])
            for a in fas.args[1:] # ignore first argument which should always be CommandContext
            if a in fas.annotations
        ]

    class AbstractENUM_STRING(object):
        values = lambda:()
        allow_other_values = False

        @classmethod
        def parse(cls, value, context):
            if value not in cls.values():
                if cls.allow_other_values:
                    context.send_feedback("accepted custom value: "+str(value))
                else:
                    raise CommandException("invalid argument value: "+repr(value))
            return str(value)

        @classmethod
        def autocomplete(cls, value, context):
            return [
                suggestion+" "
                for suggestion in cls.values()
                if suggestion.startswith(value)
            ]

    class BLOCKNAME(AbstractENUM_STRING):
        values = lambda:allBlocknames
        allow_other_values = True

    class ITEMNAME(AbstractENUM_STRING):
        values = lambda:allItemnames
        allow_other_values = True

    class GAMEMODE(AbstractENUM_STRING):
        values = lambda:("creative", "survival")

    class ENTITYNAME(AbstractENUM_STRING):
        values = lambda:entityClasses.keys()

    class ENTITY(object):
        @staticmethod
        def parse(self, context):
            for world in context.universe.worlds:
                try:
                    return world.entities[self]
                except KeyError:
                    pass
            raise CommandException("no entity with id <%s> found" % self)
            
        @staticmethod
        def autocomplete(self, context):
            entity_ids = []
            for world in context.universe.worlds:
                for entity in world.entities.entities:
                    entity_id = entity.get("id",None)
                    if entity_id and entity_id.startswith(self):
                        entity_ids.append(entity_id)
            return entity_ids
    
    class FLOAT(object):
        @staticmethod
        def parse(self, context):
            try:
                return float(self)
            except:
                raise CommandException(f"{self} is not a valid number")
        
        @staticmethod
        def autocomplete(self, context):
            return [self.rstrip()+" "] if len(self) else ["0 "] 

    class INT(object):
        def __init__(self, default=0):
            self.default = default

        @staticmethod
        def parse(value, context):
            try:
                return int(value)
            except:
                raise CommandException(f"{value} is not a valid whole number")
        
        def autocomplete(self, value, context):
            return [value.rstrip()+" "] if len(value) else [str(self.default)+" "] 
    
    class SUBCOMMAND(object):
        @staticmethod
        def parse(self, context):
            return self
        
        @staticmethod
        def autocomplete(self, context):
            return context.autocomplete(self)
    
    class FREETEXT(object):
        @staticmethod
        def parse(self, context):
            return self
        @staticmethod
        def autocomplete(self, context):
            return []

class CommandContext(object):
    @property
    def entity(self):
        if self._entity == None:
            raise CommandException("don't know which entity to target")
        return self._entity
    @entity.setter
    def entity(self, entity):
        self._entity = entity

    def __init__(self, originator):
        self.originator = originator

        if isinstance(self.originator, voxelengine.Player):
            self.originator_name = "Player " + repr(self.originator)
            if self.originator.entity:
                self.originator_name += " [%s]" % self.originator.entity["id"]
            self.permission_level = 5
            self.universe = self.originator.universe
            self.player = self.originator
            self.entity = self.originator.entity #may still be None
        elif isinstance(self.originator, voxelengine.Universe):
            self.originator_name = "Server"
            self.permission_level = 9000
            self.universe = self.originator
            self.player = None
            self.entity = None
        else:
            raise NotImplementedError()

        if self._entity:
            self.world = self.entity.world
            self.position = self.entity["position"]
        else:
            self.world = None
            self.position = None

    def send_feedback(self, feedback):
        if isinstance(self.originator, voxelengine.Player):
            self.originator.chat.add_message(feedback)
            print(feedback)
        elif isinstance(self.originator, voxelengine.Universe):
            print(feedback)
        else:
            raise NotImplementedError()

    def autocomplete(self, command_text):
        command_name, arg_text, *_ = command_text.split(" ",1) + [None]
        if arg_text == None:
            return Command.COMMAND.autocomplete(command_name, self)
        else:
            try:
                command_func = Command.COMMAND.parse(command_name, self)
            except CommandException:
                return []
            arg_layout = Command.get_arg_layout(command_func)
            # return autocompletion by type of last argument that is currently available
            l = len(arg_layout)
            args = arg_text.split(" ", l-1)
            i = len(args) - 1 # last of args but not necessarily the last of arg_layout
            last_arg_suggestions = arg_layout[i][1].autocomplete(args[i], self)
            command_except_last_arg = command_text[:len(command_text)-len(args[i])]
            return [command_except_last_arg + las for las in last_arg_suggestions] 

    def execute(self, command_text):
        try:
            command_text = command_text.rstrip(" ")
            command_name, arg_text, *_ = command_text.split(" ",1) + [""]
            command_func = Command.COMMAND.parse(command_name, self)
            # ensure permission
            if self.permission_level < command_func.permission_level:
                raise CommandException("insufficient permission level")
            # parse args
            arg_layout = Command.get_arg_layout(command_func)
            l = len(arg_layout)
            if l > 0:
                args = arg_text.split(" ", l-1)
                if len(args) != l: # should check against number of args without default value to be more precise
                    raise CommandException("wrong number of arguments")
                kwargs = {a:t.parse(args[i],self) for i,(a,t) in enumerate(arg_layout)}
                # call command_function
                command_func(self, **kwargs)
            else:
                command_func(self)
        except CommandException as e:
            error_msg = " ".join(str(a) for a in e.args)
            self.send_feedback(f"Command {command_name}: {error_msg}")

Block.subclasses = collections.defaultdict(lambda: SolidBlock, Block.subclasses)
Item.subclasses = collections.defaultdict(lambda: Item, Item.subclasses)
Entity.subclasses = collections.defaultdict(lambda: Entity, Entity.subclasses)

allBlocknames   = None # initialized in load_features_from
allItemnames    = None # initialized in load_features_from

def alias(name):
    def _alias(cls):
        assert isinstance(cls, SubclassTracker)
        SubclassTracker.register(cls, name)
        return cls
    return _alias

def register_item(name):
    def _register_item(item_subclass):
        assert issubclass(item_subclass, Item)
        assert name == item_subclass.__name__
#        if name in itemClasses:
#            print("Warning: %s replaces previous definition %s" % (item_subclass, itemClasses[name]))
#        itemClasses[name] = item_subclass
        warnings.warn("function register_item is deprecated, Item subclasses are registered automatically using their class name, further aliases can be added with the alias decorator", DeprecationWarning)
        return item_subclass
    return _register_item

def register_block(name):
    def _register_block(block_subclass):
        assert issubclass(block_subclass, Block)
        assert name == block_subclass.__name__
#        if name in blockClasses:
#            print("Warning: %s replaces previous definition %s" % (block_subclass, blockClasses[name]))
#        blockClasses[name] = block_subclass
        warnings.warn("function register_block is deprecated, Block subclasses are registered automatically using their class name, further aliases can be added with the alias decorator", DeprecationWarning)
        return block_subclass
    return _register_block

def register_entity(name):
    def _register_entity(entity_subclass):
        assert issubclass(entity_subclass, Entity)
        assert name == entity_subclass.__name__
#        if name in entityClasses:
#            print("Warning: %s replaces previous definition %s" % (entity_subclass, entityClasses[name]))
#        entityClasses[name] = entity_subclass
        warnings.warn("function register_entity is deprecated, Entity subclasses are registered automatically using their class name, further aliases can be added with the alias decorator", DeprecationWarning)
        return entity_subclass
    return _register_entity

register_command = Command.register_command

def BlockFactory(data, *args, **kwargs):
    if isinstance(data, str):
        data = {"id":data}
    block_type = data["id"]
    blockClass = Block.subclasses[block_type]
    return blockClass(data, *args, **kwargs) #M# change to directly initialize the correct block

def EntityFactory(data):
    if isinstance(data, str):
        data = {"type":data}
    entity_type = data["type"]
    entityClass = Entity.subclasses[entity_type]
    if entityClass == Entity:
        print("no entity class found for:", entity_type)
    return entityClass(data)

def ItemFactory(data):
    if isinstance(data, str):
        data = {"id":data}
    item_type = data["id"]
    itemClass = Item.subclasses[item_type]
    return itemClass(data)

texturepackDirectory = tempfile.TemporaryDirectory()
texturepackPath = texturepackDirectory.name
tp_compiler = None # initialized in load_features_from

def load_features_from(feature_paths):
    global tp_compiler, allBlocknames, allItemnames
        
    for feature_path in feature_paths:
        structure_path = os.path.join(PATH, "..", "features", feature_path, "structures")
        sys.path.append(structure_path)
        src_path = os.path.join(PATH, "..", "features", feature_path, "src")
        tree = tuple(os.walk(src_path))
        for dirpath, dirnames, filenames in tree:
            sys.path.append(dirpath)
            for fn in filenames:
                if fn.endswith(".py") and not fn.startswith("_"):
                    load_source(fn[:-3],os.path.join(dirpath,fn)) #load module from path
            sys.path.remove(dirpath)
        sys.path.remove(structure_path)

    tp_compiler = TP_Compiler()
    for feature_path in feature_paths:
        data_path = os.path.join(PATH, "..", "features", feature_path, "data")
        if os.path.isdir(data_path):
            print(data_path)
            tp_compiler.add_textures_from(data_path)
    tp_compiler.save_to(texturepackPath)

    blocks_and_block_models = dict(itertools.chain(tp_compiler.description["BLOCKS"].items(),
                                                   tp_compiler.description["BLOCK_MODELS"].items()))
    allBlocknames = tuple(blocks_and_block_models.keys())
    allItemnames = tuple(name for (name,data) in blocks_and_block_models.items() if data.get("icon"))
