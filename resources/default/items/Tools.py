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
    def use_on_block(self, character, block, face):
        return self.use_on_air(character)

    def use_on_air(self, character):
        power = 0
        pressure = None
        while pressure != 0:
            pressure = yield
            power += (pressure-power)*0.01

        print("Pling! W"+"o"*int(power*100)+"osh! Pock!")

@register_item("Saddle")
class Saddle(Item):
    def use_on_entity(self, character, entity):
        character.ride(entity)
