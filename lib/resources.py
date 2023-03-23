import sys, os, inspect, imp
import math, random, time, collections
import tempfile

PATH = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))

from TPManager.tp_compiler import TP_Compiler

import voxelengine
from voxelengine.modules.shared import *
from voxelengine.modules.geometry import Vector, Hitbox, BinaryBox, Sphere, Point, Box
from voxelengine.server.event_system import Event

GRAVITY = 35
AIRSLIDING = 1
SLIDING = 0.000001

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

class Block(voxelengine.Block):
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
        assert blockClasses[self["id"]] == type(self) #blocks must have a matching type id
    
    def turn_into(self, new_block):
        self.clear()
        if isinstance(new_block, str):
            super().__setitem__("id", new_block)
        else:
            self.update(new_block)
        self._morph()
    
    def _morph(self):
        self.__class__ = blockClasses[self["id"]]

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

    def activated(self,character,face):
        """blocks like levers should implement this action. Return value signalizes whether to execute use action of hold item"""
        return True

    def item_version(self):
        """use the output of this function when turning the block into an item"""
        return {"id":self["id"],"count":1}

    def mined(self,character,face):
        """drop item or something... also remember to set it to air. Return value see activated"""
        character.pickup_item(self.item_version())
        self.blockworld[self.position] = "AIR"
        

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
        block = BlockFactory(blockdata, position=new_pos, blockworld=character.world.blocks)
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

    def __init__(self, data = None):
        data_defaults = {
            "velocity" : Vector([0,0,0]),
            "last_update" : time.time(),
            "flying" : False,
            "lives" : 10,
            "ACCELERATION" : 20,
            "SPEED" : 10,
        }
        if data != None:
            data_defaults.update(data)
        super().__init__(data_defaults)
        
        assert type(self) != Entity #this is an abstract class, please instantiate specific subclasses or use EntityFactory
        assert entityClasses[self["type"]] == type(self) #entities must have a matching type item
        
        self.register_item_sanitizer(lambda v: Vector(v),"velocity")

        self.ai_commands = collections.defaultdict(list)

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
    def test_spawn_conditions(cls, world, position):
        block = world.blocks[position - (0,3,0)]
        area = cls.HITBOX + position
        return (block != "AIR" and not any(True for _ in world.blocks.find_blocks(area, "solid")))
    
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
    
    def execute_ai_commands(self):
        jump   = bool(sum(self.ai_commands["jump"  ]))
        shift  = bool(sum(self.ai_commands["shift" ]))
        sprint = bool(sum(self.ai_commands["sprint"]))
        x = sum(self.ai_commands["x"])
        z = sum(self.ai_commands["z"])
        self.ai_commands.clear()

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
        sv = self.horizontal_move(jump)

        target_velocity = nv*self["SPEED"]*speed_modifier
        ax, _, az = target_velocity - self["velocity"]
        a_max = self["ACCELERATION"]
        ax = max(-a_max, min(a_max, ax))
        az = max(-a_max, min(a_max, az))
        
        self["velocity"] += (ax, 0, az)

        # save previous velocity and onground
        vy_vorher = self["velocity"][1]
        onground_vorher = self.onground()
        position_vorher = self["position"]
        
        # update position
        self.update_position()
        
        # see if player hit the ground and calculate damage
        onground_nachher = self.onground()
        if (not onground_vorher) and onground_nachher:
            # Geschwindigkeit 20 entspricht etwa einer Fallhoehe von 6 Block, also ab 7 nimmt der Spieler Schaden
            schaden = (-vy_vorher) -20
            # HERZEN ANPASSEN
            if schaden > 0:
                self["lives"] -= 1
        # reset position when shifting and leaving ground
        if shift and onground_vorher and not onground_nachher:
            self["position"] = position_vorher
            self["velocity"] = Vector(0,0,0)
    
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




class Command(object):
	"""
	permission_level:
		  -1 - no commands allowed
		   0 - commands with no effects in game (whisper, help, log, etc.)
		   1 - commands with negative effects to originator (kill, ...)
		   2 - commands with slight positive effects (goto)
		   3 - commands with great positive effect (give)
		   9 - commands that directly affect other entities (entity, setblock, ...)
		  90 - commands that effect players (kick, ban, timeout, ...)
		 900 - commands that effect permissions (op, deop, ...)
		9000 - server level commands (restart, stop, etc.)
	"""
	commands = {} # {name: command_func}

	@classmethod
	def register_command(cls, name, permission_level=9000):
		def _register_command(command):
			cls.commands[name] = command
			command.permission_level = permission_level
			return command
		return _register_command

	@classmethod
	def autocomplete(cls, msg):
		return ["/"+command_name for command_name in cls.commands]

	def __init__(self, originator, command_text):
		self.originator = originator
		self.command_text = command_text

		if isinstance(self.originator, voxelengine.Player):
			self.originator_name = "Player " + repr(self.originator)
			if self.originator.entity:
				self.originator_name += " [%s]" % self.originator.entity["id"]
			self.permission_level = 3
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

		if self.entity:
			self.world = self.entity.world
			self.position = self.entity["position"]
		else:
			self.world = None
			self.position = None

	def send_feedback(self, feedback):
		if isinstance(self.originator, voxelengine.Player):
			self.originator.chat.add_message(feedback)
		print(feedback)

	def execute_subcommand(self, subcommand):
		self.command_text = subcommand
		self.execute()

	def execute(self):
		command_name, self.arg_text, *_ = self.command_text.split(" ",1) + [""]
		command_name = command_name.lstrip("/")
		command_func = self.commands.get(command_name, None)
		if command_func:
			# ensure permission
			if self.permission_level < command_func.permission_level:
				self.send_feedback("command /%s: insufficient permission level" % command_name)
				return
			# call command_function
			command_func(self)
		else:
			self.send_feedback("Command /%s is not defined" % command_name)

blockClasses    = None # initialized in load_resources_from
itemClasses     = None # initialized in load_resources_from
entityClasses   = None # initialized in load_resources_from

def register_item(name):
    def _register_item(item_subclass):
        assert issubclass(item_subclass, Item)
        if name in itemClasses:
            print("Warning: %s replaces previous definition %s" % (item_subclass, itemClasses[name]))
        itemClasses[name] = item_subclass
        return item_subclass
    return _register_item

def register_block(name):
    def _register_block(block_subclass):
        assert issubclass(block_subclass, Block)
        if name in blockClasses:
            print("Warning: %s replaces previous definition %s" % (block_subclass, blockClasses[name]))
        blockClasses[name] = block_subclass
        return block_subclass
    return _register_block

def register_entity(name):
    def _register_entity(entity_subclass):
        assert issubclass(entity_subclass, Entity)
        if name in entityClasses:
            print("Warning: %s replaces previous definition %s" % (entity_subclass, entityClasses[name]))
        entityClasses[name] = entity_subclass
        return entity_subclass
    return _register_entity

register_command = Command.register_command

def BlockFactory(data, *args, **kwargs):
    if isinstance(data, str):
        data = {"id":data}
    block_type = data["id"]
    blockClass = blockClasses[block_type]
    return blockClass(data, *args, **kwargs) #M# change to directly initialize the correct block

def EntityFactory(data):
    if isinstance(data, str):
        data = {"type":data}
    entity_type = data["type"]
    entityClass = entityClasses[entity_type]
    return entityClass(data)

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
        for directory in ("blocks","entities","items","commands"):
            path = os.path.join(PATH, ".." , "resources", resource_path, directory) #everything before resource_path is dropped in case of absolute path
            sys.path.append(path)
            if os.path.isdir(path):
                for fn in os.listdir(path):
                    if fn.endswith(".py") and not fn.startswith("_"):
                        imp.load_source(fn[:-3],os.path.join(path,fn)) #like adding to path and removing afterwards, but shorter (also it's deprecated in 3.3)
            sys.path.remove(path)
        sys.path.remove(structure_path)

    tp_compiler = TP_Compiler()
    for resource_path in resource_paths:
        textures_path = os.path.join(PATH, "..", "resources", resource_path, "textures")
        if os.path.isdir(textures_path):
            print(textures_path)
            tp_compiler.add_textures_from(textures_path)
    tp_compiler.save_to(texturepackPath)
