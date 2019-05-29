from resources import *
import tree

@register_block("DIRT")

class Dirt(Block):
    blast_resistance = 0
    def random_ticked(self):
        if self.world[self.position + (0,1,0)] == "AIR":
            self.world[self.position] = "GRASS"

@register_block("GRASS")
class Grassblock(Block):
    def random_ticked(self):
        for other in ["AIR","grass","LilaBlume","WeisseBlume","RoteBlume","BlaueBlume","GelbeBlume","SonnenBlume"]:
            if self.world[self.position+(0,1,0)] == other:
                if random.random()<0.008:
                    self.world[self.position+(0,1,0)] = random.choice(["grass","grass","grass","grass",
                                                                       "LilaBlume","WeisseBlume","RoteBlume",
                                                                       "BlaueBlume","GelbeBlume","SonnenBlume"])
                break
        else:
            self.world[self.position] = "DIRT"
            

@register_block("grass")
@register_block("LilaBlume")
@register_block("WeisseBlume")
@register_block("BlaueBlume")
@register_block("RoteBlume")
@register_block("GelbeBlume")
@register_block("SonnenBlume")
class Plant(Block):
    def collides_with(self,hitbox,position):
        return False


@register_block("Setzling")

class Setzling(Block):
    blast_resistance = 0
    def random_ticked(self):
        for d_pos, block in tree.tree_structure("eiche"):
            self.world[self.position+d_pos-(0,1,0)] = block
    def collides_with(self,hitbox,position):
        return False
