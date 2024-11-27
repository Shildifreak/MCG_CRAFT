from resources import *
from voxelengine.modules.geometry import Vector, Hitbox, Point
from voxelengine.server.event_system import Event

class FIRE(Block):
    def handle_event_entity_enter(self,events):
        for event in events:
            entity = event.data
            if entity["type"] != "Burn":
                EntityFactory("Burn").set_target(entity)
        return False

    def get_tags(self):
        return (super().get_tags() - {"solid"}) | {"entity_enter"}

class Burn(Entity):
    HITBOX = Hitbox(1,2,1.5)
    LIMIT = 0
    TTL = 5
    DAMAGE_DELAY = 1 # damage target every DAMAGE_DELAY seconds
    DAMAGE_AMOUNT = 1
    instances = []

    def __init__(self, data = None):
        data_defaults = {
            "texture" : "BURN",
#            "SPEED" : 1,
#            "JUMPSPEED" : 10,
#            "forward" : False,
#            "turn" : 0,
            "tags" : {"update"},
            "ttl" : self.TTL,
            "t_damage" : self.TTL,
        }
        if data != None:
            data_defaults.update(data)
        super().__init__(data_defaults)
        self.target = None

    def set_target(self, entity):
        self.target = entity
        self.set_world(entity.world, entity["position"])

    def update(self):
        # check for exit condition
        self["ttl"] -= self.dt
        if (not self.target) or (self["ttl"] < 0) or self.inwater():
             self.kill()
             return
        # damage target
        if self["t_damage"] - self["ttl"] > self.DAMAGE_DELAY:
            self["t_damage"] = self["ttl"]
            self.target.take_damage(self.DAMAGE_AMOUNT)
        # animate
        y,p = self["rotation"]
        y += 1
        self["rotation"] = (y,p)
        self["position"] = self.target["position"]
        self.update_position()

#    def clicked(self, character, item):
#        r = character.get_sight_vector()
#        self["velocity"] = Vector(r)*(20,0,20) + Vector((0,15,0))
#        sound_event = Event("sound",Point(self["position"]),"cat1")
#        self.world.event_system.add_event(sound_event)
