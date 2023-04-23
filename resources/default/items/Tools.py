from resources import *
import resources
import random


@register_item("Axe")
class Fertilizer(Item):
    def use_on_block(self, character, blockpos, face):
        character.world.blocks[blockpos].mined(character, face)

    def use_on_entity(self, character, entity):
        entity.damage(5)
        #self.decrease_count()

@register_item("Fishing_Rod")
class Fertilizer(Item):
    def use_on_block(self, character, blockpos, face):
        if character.world.blocks[blockpos] == "WATER":
            blockname = random.choice(resources.allBlocknames)
            character.pickup_item({"id":blockname})

    def use_on_entity(self, character, entity):
        print("Pull Entity!")

@register_item("Bow")
class Fertilizer(Item):
    def use_on_block(self, character, blockpos, face):
        self.use_on_air()

    def use_on_air(self, character):
        print("Pling! Woosh! Pock!")
