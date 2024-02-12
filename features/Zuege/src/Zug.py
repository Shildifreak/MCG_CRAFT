from resources import *
import random

@register_entity("Zug")
class Zug(Entity):
    HITBOX = Hitbox(3,4,2)
    LIMIT = 0
    instances = []
    PASSENGER_OFFSETS = [Vector(0,0.8,i) for i in range(4)]
    
    def __init__(self, data = None):
        data_defaults = {
            "texture" : "ZUG",
            "SPEED" : 10,
            "JUMPSPEED" : 10,
            "tags" : {"update"},
            "richtung" : Vector(0,0,1),
        }
        if data != None:
            data_defaults.update(data)
        super().__init__(data_defaults)

    def clicked(self, character, item):
        print("Einsteigen bitte!")
        character.ride(self)

    def update(self):
        wir_haben_schienen = False
        offset = Vector(0, -2, 0)
        for abstand in range(3):
            blockpos = self["position"].round() + abstand*self["richtung"] + offset
            if self.world.blocks[blockpos] == "Schiene_Schwelle":
                wir_haben_schienen = True
        if wir_haben_schienen == True:
            self["position"] += self["richtung"] * len(self.passengers) * self["SPEED"] * self.dt
        if wir_haben_schienen == False:
            #drehe dich 180° JETZT!!!
            self["richtung"] = self["richtung"] * -1
            #self["SPEED"] = self["SPEED"] * 2

@register_entity("Zuuug")
class Zuuug(Zug):
    def __init__(self, data = None):
        super().__init__(data)
        self["texture"] = "ZUUUG"

@register_item("Zug")
class ZugItem(Item):
    def use_on_block(self, character, block, face):
        print("using Zug")
        z = EntityFactory({"type":"Zug"})
        z.set_world(block.world, block.position+(0,3,0))

@register_item("Zuuug")
class ZuuugItem(ZugItem):
    def use_on_block(self, character, block, face):
        z = EntityFactory({"type":"Zuuug"})
        z.set_world(block.world, block.position+(0,3,0))
