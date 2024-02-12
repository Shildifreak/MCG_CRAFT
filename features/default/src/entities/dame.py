from resources import *
import time, random

@register_entity("DAME")

class Dame(Entity):
    HITBOX = Hitbox(0.6,3,1.5)
    LIMIT = 0
    instances = []
    
    def __init__(self):
        super(Dame,self).__init__()

        self["texture"] = "DAME"
        self["SPEED"] = 1.3
        self["JUMPSPEED"] = 10
        self["sprint"] = 20
        self["tags"] = {"update"}

    def update(self):
        if self.world.players:
            player = random.choice(tuple(self.world.players))
            richtung = player.entity["position"] - self["position"]
            self["velocity"] = richtung.normalize() * self["SPEED"]
        else:
            self["velocity"] = Vector((0,0,0))
        self.update_position()
