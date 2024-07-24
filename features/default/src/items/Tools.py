from resources import *
from voxelengine.modules.geometry import Ray
import resources
import random
import time


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


class InstaPick(Axe):
    TTM = 0


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


class Fishing_Rod(UnplacableItem):
    max_distance = 5

    def use_on_air(self, character):
        line_of_sight = Ray(character["position"], character.get_sight_vector())
        def blocktest(pos):
            block = character.world.blocks[pos]
            return block.collides_with(line_of_sight) or block == "WATER"
        d_block, pos, face = line_of_sight.hit_test(blocktest, self.max_distance)
        if pos:
            block = character.world.blocks[pos]
            if block == "WATER":
                blockname = random.choice(resources.allBlocknames)
                character.pickup_item({"id":blockname})

    def use_on_entity(self, character, entity):
        print("Pull Entity!")


class Bow(UnplacableItem):
    MAXPOWER = 40

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
                entity["velocity"] = (entity["velocity"]+self["velocity"])*(1,0,1) + (0,10,0)
                self.kill()
                return

        if self.onground():
            self.kill()
            return


class Saddle(Item):
    def use_on_entity(self, character, entity):
        character.ride(entity)


class BallEmpty(Item):
    def use_on_entity(self, character, entity):
        entity.set_world(None,(0,0,0))
        entity = serialize(entity, (Vector, Box, Sphere, Event))
        self.decrease_count()
        character.pickup_item({"id":"BallFull", "entity":entity})


class BallFull(Item):
    def use_on_air(self, character):
        self._use(character, character["position"]+character.get_sight_vector()*3)

    def use_on_block(self, character, block, face):
        self._use(character, block.position+(0,2,0))
        
    def _use(self, character, position):
        if "entity" in self.item:
            entity = serialize(self.item.pop("entity"), (Vector, Box, Sphere, Event))
            entity = EntityFactory(entity)
            entity.set_world(character.world, position)
        self.decrease_count()
        character.pickup_item({"id":"BallEmpty"})

class Bucket(UnplacableItem):
    max_distance = 5

    def use_on_air(self, character):
        line_of_sight = Ray(character["position"], character.get_sight_vector())
        def blocktest(pos):
            block = character.world.blocks[pos]
            return block.collides_with(line_of_sight) or block == "WATER"
        d_block, pos, face = line_of_sight.hit_test(blocktest, self.max_distance)
        if pos:
            block = character.world.blocks[pos]
            if block == "WATER":
                character.world.blocks[pos] = "AIR"
                self.decrease_count()
                character.pickup_item({"id":"BucketOfWater"})

class BucketOfWater(Item):
    def block_version(self):
        """use the output of this function when trying to place the item into the world as a block"""
        return "WATER"
    
    def place(self, character, block, face):
        super().place(character, block, face)
        character.pickup_item({"id":"Bucket"})
