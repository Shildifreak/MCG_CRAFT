from resources import *
import time, random

@register_entity("Item")

class ItemEntity(Entity):
    HITBOX = Hitbox(0.4, 0.4, 0.4)
    LIMIT = 5 # no natural Spawning of Item Entities
    instances = []
    
    def __init__(self, data = None):
        data_defaults = {
            "texture" : "ITEM",
            "show_emote" : False,
            "lives" : 1,
            "tags" : {"update"},
            "item" : {"id":"GRASS"},
        }
        if data != None:
            data_defaults.update(data)
        super().__init__(data_defaults)
        
        self.register_item_callback(self._update_modelmaps,"item")

    def _update_modelmaps(self, _):
        modelmaps = {"<<item>>":ItemFactory(self["item"]).entity_blockmodel()}
        self["modelmaps"] = modelmaps

    def right_clicked(self, character):
        self.collect_by(character)

    def left_clicked(self, character):
        self.collect_by(character)

    def collect_by(self, character):
        if character.pickup_item(self["item"]):
            self.kill()

    def update(self):
        if self.onground():
            #self["velocity"] += (0,10,0)
            pass
        else:
            self["velocity"] -= (0,1,0)
        self.update_dt()
        self.update_position()
