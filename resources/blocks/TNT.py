from resources import *
import random

@register_block("TNT")
class tntblock(Block):
    blast_resistance =  0
    power_min = 3
    power_max = 7

    def handle_event_block_update(self,events):
        for face in FACES:
            nachbarblock = self.relative[face]
            if nachbarblock["p_level"] > 0:
                self.explode()
                break

    def activated(self,character,face):
        self.explode()

    def explode(self):
        self.world.blocks[self.position] = "AIR"
        power = random.randint(self.power_min,self.power_max)
        explosion_event = Event("explosion",Sphere(self.position,power))
        self.world.event_system.add_event(0, explosion_event)
        
    def handle_event_explosion(self,events):
        self.explode()

    def get_tags(self):
        return super().get_tags() + {"block_update"}

@register_block("A-TNT")
class a_tntblock(tntblock):
    power_min = 14
    power_max = 16

@register_block("B-TNT")
class b_tntblock(tntblock):

    def explode(self):
        self.world.blocks[self.position] = "AIR"
        power = random.randint(14,16)
        lower_bounds = self.position + (-power, -1, -power)
        upper_bounds = self.position + (+power, -1, +power)
        area = Box(lower_bounds, upper_bounds)
        explosion_event = Event("explosion",area)
        self.world.event_system.add_event(0, explosion_event)
