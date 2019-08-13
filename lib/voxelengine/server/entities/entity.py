import sys, os
if __name__ == "__main__":
    sys.path.append(os.path.abspath("../../.."))
    print(sys.path)
    __package__ = "voxelengine.server.entities"

import math
from voxelengine.modules.observableCollections import ObservableDict
from voxelengine.modules.shared import Vector
import voxelengine.modules.collision_forms as collision_forms
from voxelengine.server.event_system import Event

class Entity(ObservableDict):
    def __init__(self,data = None):
        ObservableDict.__init__(self,data if data != None else {})
        self.world = None
        self._old_position = None
        
        self.setdefault("position",(0,0,0))
        self.setdefault("rotation",(0,0))
        self.setdefault("texture",0)
        self.setdefault("speed",5)
        self.setdefault("tags",[])

        self.register_item_callback(self._on_position_change,"position")
        self.register_item_callback(self._on_tags_change,"tags")
        self.register_item_callback(self._notify_chunk_observers,"rotation")
        self.register_item_callback(self._notify_chunk_observers,"texture")
        self.register_item_sanitizer(lambda pos: Vector(pos),"position")

        self.HITBOX = collision_forms.Point((0,0,0)) #M# tmp, should be replaced with list of collision forms and corresponding action

    def _on_position_change(self, new_position):
        """set position of entity"""
        old_position = self._old_position
        self._old_position = new_position

        if self.world:
            # tell entity system that entity has moved
            self.world.entities.notice_move(self,old_position,new_position)
            
            # tell everyone listening that entity has moved
            self.world.event_system.add_event(0,Event("entity_leave",self.HITBOX+old_position,self))
            self.world.event_system.add_event(0,Event("entity_enter",self.HITBOX+new_position,self))

    def _on_tags_change(self, new_tags):
        if self.world:
            self.world.entities.change_tags(self)

    def set_world(self, new_world, new_position):
        """ leave old world, change position, enter new world """
        # leave old world
        if self.world:
            self.world.entities.remove(self)
            self.world.event_system.add_event(0,Event("entity_leave",self.HITBOX+self["position"],self))
        self.world = None

        # change position
        self["position"] = new_position

        # enter new world
        self.world = new_world
        if self.world:
            self.world.entities.add(self)
            self.world.event_system.add_event(0,Event("entity_enter",self.HITBOX+self["position"],self))
        
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
    
    def handle_events(self, events):
        pass

    def _notify_chunk_observers(self,*_):
        if self.world:
            self.world.event_system.add_event(0,Event("entity_move",self.HITBOX+self["position"],self))

if __name__ == "__main__":
    e = Entity()
