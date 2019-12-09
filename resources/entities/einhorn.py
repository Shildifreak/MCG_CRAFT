from resources import *
import time, random

@register_entity("Einhorn")

class Einhorn(Entity):
    HITBOX = Hitbox(0.6,1.5,1)
    LIMIT = 1
    instances = []
    
    def __init__(self):
        super(Einhorn,self).__init__()
        
        self["texture"] = "EINHORN"
        self["SPEED"] = 5
        self["JUMPSPEED"] = 10
        self["sprint"] = 20
        self["forward"] = False
        self["turn"] = 0

    def right_clicked(self, character):
        self["texture"] = "SCHAF"
        
    def left_clicked(self, character):
        self["texture"] = "SCHAF"

    def update(self):
        pass
