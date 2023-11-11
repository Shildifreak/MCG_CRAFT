from resources import *
import resources
import random
import time

@register_item("Axe")
class Axe(Item):
    TTM = 0.2
    def use_on_block(self, character, block, face):
        t0 = time.time()
        while time.time() - t0 < self.TTM:
            pressure = yield
        block.mined(character, face)

    def use_on_entity(self, character, entity):
        entity.take_damage(5)
        #self.decrease_count()

@register_item("InstaPick")
class InstaPick(Axe):
    TTM = 0

@register_item("InfiniPick")
class InfiniPick(Item):
    """A Pickaxe that continues mining as long as the key/button is held down."""
    max_distance = 5
    interval = 0.05
    def use_on_block(self, character, block, face):
        block.mined(character, face)
        yield from wait(0.2)
        yield from self.use_on_air(character)
    
    def use_on_air(self, character):
        while True:
            pressure = yield
            distance, pos, face = character.get_focused_pos(self.max_distance)
            if pos:
                block = character.world.blocks[pos]
                block.mined(character, face)
                yield from wait(self.interval)

@register_item("Fishing_Rod")
class FishingRod(Item):
    def use_on_block(self, character, block, face):
        if block == "WATER":
            blockname = random.choice(resources.allBlocknames)
            character.pickup_item({"id":blockname})

    def use_on_entity(self, character, entity):
        print("Pull Entity!")

@register_item("Bow")
class Bow(Item):
    MAXPOWER = 40

    def use_on_block(self, character, block, face):
        return self.use_on_air(character)

    def use_on_air(self, character):
        power = 0.3
        pressure = None
        while pressure != 0:
            pressure = yield
            direction = 1 if pressure > power else -1
            delta = direction*character.dt
            limit = abs(pressure-power)
            power += max(-limit,min(+limit,delta))

        if power < 0.3:
            return
        arrow = EntityFactory({"type":"Arrow"})
        arrow.set_world(character.world, character["position"]+character.get_sight_vector()*2)
        arrow["rotation"] = character["rotation"]
        arrow["velocity"] = character.get_sight_vector() * power * self.MAXPOWER

@register_entity("Arrow")
class Arrow(Entity):
    HITBOX = Hitbox(1,1,0.5)
    LIMIT = 0
    instances = []
    
    def __init__(self, data = None):
        data_defaults = {
            "texture" : "ARROW",
            "tags" : {"update"},
        }
        if data != None:
            data_defaults.update(data)
        super().__init__(data_defaults)

    def update(self):
        #self.set_sight_vector(self["velocity"])
        y,p = self["rotation"]
        self["rotation"] = (y,p-90*self.dt)
        self["velocity"] -= Vector(0, GRAVITY, 0) * self.dt
        self.update_position()
        
        area = self.HITBOX + self["position"]
        for entity in self.world.entities.find_entities(area):
            if entity != self:
                entity.take_damage(3)
                entity["velocity"] += self["velocity"]
                self.kill()
                return

        if self.onground():
            self.kill()
            return

@register_item("Saddle")
class Saddle(Item):
    def use_on_entity(self, character, entity):
        character.ride(entity)
