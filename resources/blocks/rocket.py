from resources import *

@register_block("ROCKET")
class Rocket(Block):
    blast_resistance = 1
    delay = 10

    def handle_event_block_update(self,event):
        self.world.events.add("rocket_move",Point(self.position),delay)
        
    def handle_event_rocket_move(self,event):
        v = self.get_front_facing_vector()
        if self.world[self.position+v] == "AIR":
            self.world[self.position+v] = {"id":"ROCKET","rotation":self["rotation"],"base":self["base"]}
            self.world[self.position] = "AIR"
            # add move request with callbacks here instead
            self.world.events.add("rocket_move",Point(self.position),delay)
        else:
            # schedule explode event here
            tntrange = random.randint(3,7)
            self.world[self.position] = "AIR"
            for dx in range(-tntrange,tntrange+1):
                for dy in range(-tntrange,tntrange+1):
                    for dz in range(-tntrange,tntrange+1):
                        tp = self.position+(dx,dy,dz)
                        dp = type(self.position)((dx,dy,dz))
                        self.world[tp].exploded(dp.length()/tntrange)
    
    def get_tags(self):
        return super(Redstone,self).get_tags().union({"block_update"})
