import sys, os
if __name__ == "__main__":
    sys.path.append(os.path.abspath("../../.."))
    print(sys.path)
    __package__ = "voxelengine.server.entities"

import math
from voxelengine.modules.observableCollections import ObservableDict
from voxelengine.modules.geometry import Vector, Point, Ray
from voxelengine.server.event_system import Event

class Entity(ObservableDict):
    __slots__ = ("world","_position_buffer")
    HITBOX = Point((0,0,0)) #M# tmp, should be replaced with list of collision forms and corresponding action

    def __init__(self,data = None):
        assert type(self) != Entity #this is an abstract class, please instantiate specific subclasses

        data_defaults = {
            "position" : (0,0,0),
            "rotation" : (0,0),
            "texture" : 0,
            "tags" : [],
        }
        if data != None:
            data_defaults.update(data)
        super().__init__(data_defaults)

        self.world = None
        self._position_buffer = None
        
        self.register_item_callback(self._on_position_change,"position")
        self.register_item_callback(self._on_tags_change,"tags")
        self.register_item_callback(self._on_visible_change,"rotation")
        self.register_item_callback(self._on_visible_change,"texture")
        self.register_item_sanitizer(lambda pos: Vector(pos),"position")

    def _on_position_change(self, new_position):
        """set position of entity"""
        old_position = self._position_buffer
        self._position_buffer = new_position

        if self.world:
            # tell entity system that entity has moved
            self.world.entities.notice_move(self,old_position,new_position)
            
            # tell everyone listening that entity has moved
            self.world.event_system.add_event(Event("entity_leave",self.HITBOX+old_position,self))
            self.world.event_system.add_event(Event("entity_enter",self.HITBOX+new_position,self))

    def _on_tags_change(self, new_tags):
        if self.world:
            self.world.entities.change_tags(self)

    def set_world(self, new_world, new_position):
        """ leave old world, change position, enter new world """
        # leave old world
        if self.world:
            self.world.entities.remove(self)
            self.world.event_system.add_event(Event("entity_leave",self.HITBOX+self["position"],self))
        self.world = None

        # change position
        self["position"] = new_position

        # enter new world
        self.world = new_world
        if self.world:
            self.world.entities.add(self)
            self.world.event_system.add_event(Event("entity_enter",self.HITBOX+self["position"],self))
        
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
    
    def get_focused_pos(self, max_distance):
        """Line of sight search from current position. If a block is
        intersected it's position is returned, along with the face and distance:
            (distance, position, face)
        If no block is found, return (None, None, None).

        max_distance : How many blocks away to search for a hit.
        """ 
        line_of_sight = Ray(self["position"], self.get_sight_vector())
        return line_of_sight.hit_test(lambda v,b=self.world.blocks: b[v]!="AIR", max_distance)

    def get_focused_entity(self, max_distance):
        """Line of sight search from current position. If an entity is
        intersected it is returned, along with the distance:
            (distance, entity)
        If no entity is found, return (None, None).

        max_distance : How many blocks away to search for a hit."""
        nearest_entity = None
        line_of_sight = Ray(self["position"],self.get_sight_vector())
        for entity in self.world.entities.find_entities(line_of_sight.bounding_box(max_distance)):
            if entity is self:
                continue
            d = line_of_sight.distance_from_origin_to_Box(entity.HITBOX+
                                                          entity["position"]
                                                          )
            if (d != False) and (d < max_distance):
                nearest_entity = entity
                max_distance = d
        if nearest_entity:
            return max_distance, nearest_entity
        return (None, None)

    
    def handle_events(self, events):
        pass

    def _on_visible_change(self,*_):
        if self.world:
            self.world.event_system.add_event(Event("entity_change",self.HITBOX+self["position"],self))

class GenericEntity(Entity):
    __slots__ = ()

if __name__ == "__main__":
    e = GenericEntity()
