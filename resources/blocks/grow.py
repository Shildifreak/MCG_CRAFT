from resources import *
import tree

@register_block("DIRT")

class Dirt(Block):
    blast_resistance = 0
    def random_ticked(self):
        if self.world[self.position + (0,1,0)] == "AIR":
            self.world[self.position] = "GRASS"

    def get_tags(self):
        return super(Dirt,self).get_tags().union({"random_tick"})

@register_block("Setzling")

class Setzling(Block):
    blast_resistance = 0
    def random_ticked(self):
        for d_pos, block in tree.tree_structure("eiche"):
            self.world[self.position+d_pos-(0,1,0)] = block

    def get_tags(self):
        return super(Setzling,self).get_tags().union({"random_tick"}) - {"solid"}

    def collides_with(self,area):
        return False
