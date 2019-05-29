from resources import *
import random

@register_block("WAND")

class Wand(Block):
    def collides_with(self,hitbox,position):
        return False


@register_block("AIM")
class Aim(Block):
    blast_resistance = 1
    def random_ticked(self):
        if random.random() > 0.9:
            x,y,z = self.position
            self.world[(x,y+1,z)] = "STONE"
            self.world[(x,y+2,z)] = "GESICHT"
