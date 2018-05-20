from resources import *
import time, random

@register_entity("Einhorn")

class Einhorn(Entity):
    HITBOX = get_hitbox(0,0,0)
    LIMIT = 5
    instances = []
    
    def __init__(self,world):
        super(Einhorn,self).__init__()
        
        self["texture"] = "EINHORN"
        self["SPEED"] = 5
        self["JUMPSPEED"] = 10
        self["sprint"] = 20
        self["velocity"] = Vector([0,0,0])
        self["last_update"] = time.time()
        self["forward"] = False
        self["turn"] = 0

    def update(self):
        pass
