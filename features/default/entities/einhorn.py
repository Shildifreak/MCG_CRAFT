from resources import *
import time, random

@register_entity("Einhorn")

class Einhorn(Entity):
    HITBOX = Hitbox(0.6,1.5,1)
    LIMIT = 1
    instances = []
    
    def __init__(self, data = None):
        data_defaults = {
            "texture" : "EINHORN",
            "SPEED" : 5,
            "JUMPSPEED" : 10,
            "sprint" : 20,
            "forward" : False,
            "turn" : 0,
            "tags" : {"random_tick_source"},
        }
        if data != None:
            data_defaults.update(data)
        super().__init__(data_defaults)
        

    def clicked(self, character, item):
        self["texture"] = "SCHAF"

    def update(self):
        pass
