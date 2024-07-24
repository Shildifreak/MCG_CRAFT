from resources import *
import random

class TNT(Block):
    blast_resistance =  0
    power_min = 3
    power_max = 7

    def handle_event_block_update(self,events):
        for face in FACES:
            nachbarblock = self.relative[face]
            if nachbarblock["p_level"] > 0:
                self.explode()
                return True
        return False

    def clicked(self,character,face,item):
        self.explode()
        self.save()

    def explode(self):
        power = random.randint(self.power_min,self.power_max)
        explosion_event = Event("explosion",Sphere(self.position,power))
        self.world.event_system.add_event(explosion_event)
        self.turn_into("AIR")
        
    def handle_event_explosion(self,events):
        self.explode()
        return True

    def get_tags(self):
        return super().get_tags() | {"block_update"}

@alias("A-TNT")
class _a_tntblock(TNT):
    power_min = 14
    power_max = 16

@alias("B-TNT")
class _b_tntblock(TNT):

    def explode(self):
        power = random.randint(14,16)
        lower_bounds = self.position + (-power, -1, -power)
        upper_bounds = self.position + (+power, -1, +power)
        area = Box(lower_bounds, upper_bounds)
        explosion_event = Event("explosion",area)
        self.world.event_system.add_event(explosion_event)
        self.turn_into("AIR")
