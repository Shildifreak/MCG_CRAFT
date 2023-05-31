from resources import *
from voxelengine.modules.geometry import Vector, Hitbox, Point
from voxelengine.server.event_system import Event

@register_entity("Geist")

class Geist(Entity):
    HITBOX = Hitbox(1.49,2.99,1.49)
    LIMIT = 1
    instances = []

    def __init__(self, data = None):
        data_defaults = {
            "texture" : "GEIST",
            "SPEED" : 1,
            "JUMPSPEED" : 10,
            "forward" : False,
            "turn" : 0,
            "tags" : {"update"},
        }
        if data != None:
            data_defaults.update(data)
        super().__init__(data_defaults)

    def update(self):
        if self["position"][1] < -100:
            self.kill()
            return
       
        vx,vy,vz=self["velocity"]

        vy=vy-1

        if self.onground():
            vy = self["JUMPSPEED"]

        self["velocity"] = Vector((vx*self["SPEED"],vy,vz*self["SPEED"]))
            
        self.update_position()

    def clicked(self, character, item):
        r = character.get_sight_vector()
        self["velocity"] = Vector(r)*(20,0,20) + Vector((0,15,0))
        sound_event = Event("sound",Point(self["position"]),"cat1")
        self.world.event_system.add_event(sound_event)
