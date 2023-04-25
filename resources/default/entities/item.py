from resources import *
import time, random

@register_entity("Item")

class ItemEntity(Entity):
    HITBOX = Hitbox(0.4, 0.4, 0.2)
    LIMIT = 0 # no natural Spawning of Item Entities
    instances = []
    TTL = 10
    
    def __init__(self, data = None):
        data_defaults = {
            "texture" : "ITEM",
            "show_emote" : False,
            "lives" : 1,
            "tags" : {"update", "entity_enter"},
            "item" : {"id":"missing_texture"},
        }
        if data != None:
            data_defaults.update(data)
        super().__init__(data_defaults)
        
        self.register_item_callback(self._update_modelmaps,"item")

    def _update_modelmaps(self, _):
        modelmaps = {"<<item>>":ItemFactory(self["item"]).entity_blockmodel()}
        self["modelmaps"] = modelmaps

    def clicked(self, character, item):
        self.collect_by(character)

    def collect_by(self, character):
        if character.pickup_item(self["item"]):
            self.kill()
    
    def add_random_velocity(self):
        self["tags"] = {"update", "entity_enter"}
        self["velocity"] += (random.normalvariate(0,2),
                             random.normalvariate(10,2),
                             random.normalvariate(0,2))

    def handle_event_random_tick(self, events):
        self.add_random_velocity()

    def handle_event_block_update(self, events):
        self["tags"] = {"update", "entity_enter"}

    def handle_event_entity_enter(self, events):
        for event in events:
            entity = event.data
            if entity["type"] == "Mensch":
                self.collect_by(entity)
                return

    def update(self):
        if self.onground():
            self["velocity"] = (0,0,0)
            self["tags"] = {"block_update", "random_tick", "entity_enter"}
        else:
            self["velocity"] -= (0,1,0)
            self["rotation"] = (self["rotation"][0]+10, 0)
            self.update_position()
        self.take_damage(self.dt/self.TTL)
