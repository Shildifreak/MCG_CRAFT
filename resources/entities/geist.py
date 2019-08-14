from resources import *
from voxelengine.modules.geometry import Vector, Hitbox

@register_entity("Geist")

class Geist(Entity):
    HITBOX = Hitbox(0.6,1.5,1)
    LIMIT = 1
    instances = []

    def __init__(self):
        super(Geist,self).__init__()

        self["texture"] = "GEIST"
        self["SPEED"] = 5
        self["JUMPSPEED"] = 10
        self["forward"] = False
        self["turn"] = 0

    def update(self):
        self.update_dt()
       
        vy=self["velocity"][1]

        vy=vy-1

        if self.onground():
            vy = 6

        self["velocity"] = Vector((1,vy,0))
            
        self.update_position()
