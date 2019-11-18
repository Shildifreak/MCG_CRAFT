from resources import *
import time, random

@register_entity("Mensch")

class Mensch(Entity):
    HITBOX = Hitbox(0.4, 1.8, 1.6)
    LIMIT = 0 # no natural Spawning of Player Characters ;)
    instances = []
    
    def __init__(self, *args, **kwargs):
        super(Mensch,self).__init__()

        self["texture"] = "MENSCH"
        self["SPEED"] = 11
        self["FLYSPEED"] = 11
        self["JUMPSPEED"] = 10
        self["inventory"] = []
        self["left_hand"] = {"id":"AIR"}
        self["right_hand"] = {"id":"AIR"}
        self["open_inventory"] = False #set player.entity.foreign_inventory then trigger opening by setting this attribute
        self["lives"] = 9
        self["tags"] = {"random_tick_source"}

    def right_clicked(self, character):
        print("Oh no, that hurts!")
        
    def left_clicked(self, character):
        print("Just stop it already!")

    def update(self):
        pass
