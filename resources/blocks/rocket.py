from resources import *

@register_block("ROCKET")
class Rocket(Block):
    blast_resistance = 1
    

    def block_update(self,*args):
        v = self.get_front_facing_vector()
        if self.world[self.position+v] == "AIR":
            self.world[self.position+v] = {"id":"ROCKET","rotation":self["rotation"],"base":self["base"]}
            self.world[self.position] = "AIR"
        else:
            tntrange = random.randint(3,7)
            self.world[self.position] = "AIR"
            for dx in range(-tntrange,tntrange+1):
                for dy in range(-tntrange,tntrange+1):
                    for dz in range(-tntrange,tntrange+1):
                        tp = self.position+(dx,dy,dz)
                        dp = type(self.position)((dx,dy,dz))
                        self.world[tp].exploded(dp.length()/tntrange)
    

@register_block("RACKETENWERFER")
class Rocketlauncher(Block):
    blast_resistance = 0
    

    def activated(self,*args):
        v = self.get_front_facing_vector()
        if self.world[self.position+v] == "AIR":
            self.world[self.position+v] = {"id":"ROCKET","rotation":self["rotation"],"base":self["base"]}
