from base import *

@register_block("DIRT")

class Dirt(Block):
    blast_resistance = 0
    def random_ticked(self):
        self.world[self.position] = "GRASS"
