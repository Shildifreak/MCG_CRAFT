from resources import *
import random

@register_entity("Zug")
class Zug(Entity):
    HITBOX = Hitbox(3,4,2)
    LIMIT = 0
    instances = []
    
    def __init__(self, data = None):
        data_defaults = {
            "texture" : "ZUG",
            "SPEED" : 68,
            "JUMPSPEED" : 10,
            "tags" : {"update"},
        }
        if data != None:
            data_defaults.update(data)
        super().__init__(data_defaults)
        self.mitfahrer = []

    def clicked(self, character, item):
        print("Einsteigen bitte!")
        if character in self.mitfahrer:
            self.mitfahrer.remove(character)
        else:
            self.mitfahrer.append(character)

    def update(self):
        self["position"] += Vector(0,0,1) * len(self.mitfahrer) * self["SPEED"] * self.dt
        for i, character in enumerate(self.mitfahrer):
            character["position"] = self["position"]+(0,0.8,i)

@register_item("Zug")
class ZugItem(Item):
    def use_on_block(self, character, block, face):
        z = EntityFactory({"type":"Zug"})
        z.set_world(block.world, block.position+(0,3,0))
