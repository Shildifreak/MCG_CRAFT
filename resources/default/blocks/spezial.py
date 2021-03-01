from resources import *
import random

@register_block("WAND")

class Wand(Block):
    def collides_with(self,area):
        return False

    def get_tags(self):
        return super().get_tags() - {"solid"}


@register_block("AIM")
class Aim(Block):
    blast_resistance = 1
    def handle_event_random_tick(self,events):
        if random.random() > 0.9:
            x,y,z = self.position
            self.world.request_set_block((x,y+1,z), "STONE")
            self.world.request_set_block((x,y+2,z), "GESICHT")
        return False

    def get_tags(self):
        return super().get_tags() | {"random_tick"}
