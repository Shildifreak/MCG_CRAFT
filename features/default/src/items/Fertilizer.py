from resources import *
import random


class Fertilizer(Item):
    def use_on_block(self, character, block, face):
        character.world.random_tick_at(block.position)
        self.decrease_count()

    def use_on_entity(self, character, entity):
        character.world.random_tick_at(entity["position"])
        self.decrease_count()
    
    def use_on_air(self, character):
        radius = 8
        blockworld = character.world.blocks
        area = Sphere(character["position"], radius)
        tickable_blocks = tuple(blockworld.find_blocks(area, "random_tick"))
        if tickable_blocks:
            block = random.choice(tickable_blocks)
            if random.random() < 0.8:
                character.world.random_tick_at(block.position)
            self.decrease_count()
