from resources import *
import tree

@register_block("DIRT")

class Dirt(Block):
    blast_resistance = 0
    def handle_event_random_tick(self):
        if self.world[self.position + (0,1,0)] == "AIR":
            self.world[self.position] = "GRASS"

    def get_tags(self):
        return super(Dirt,self).get_tags().union({"random_tick"})

@register_block("GRASS")
class Grassblock(Block):
    def handle_event_random_tick(self):
        if self.relative[(0,1,0)] == "AIR":
            if random.random()<0.008:
                self.relative[(0,1,0)] = random.choice(["grass","grass","grass","grass",
                                                                       "LilaBlume","WeisseBlume","RoteBlume",
                                                                       "BlaueBlume","GelbeBlume","SonnenBlume"])
        elif self.relative[(0,1,0)] not in ["AIR","grass","LilaBlume","WeisseBlume","RoteBlume","BlaueBlume","GelbeBlume","SonnenBlume"]:
            self.world.blocks[self.position] = "DIRT"
    def get_tags(self):
        return super(Grassblock,self).get_tags().union({"random_tick"})
            

@register_block("grass")
@register_block("LilaBlume")
@register_block("WeisseBlume")
@register_block("BlaueBlume")
@register_block("RoteBlume")
@register_block("GelbeBlume")
@register_block("SonnenBlume")
class Plant(Block):
    def collides_with(self,area):
        return False
    def handle_event_block_update(self,events):
        if self.relative[(0,-1,0)] != "GRASS":
            self.world.blocks[self.position] = "AIR"
    def get_tags(self):
        return super(Plant,self).get_tags().union({"block_update"})-{"solid"}


@register_block("Setzling")

class Setzling(Block):
    blast_resistance = 0
    def handle_event_random_tick(self):
        for d_pos, block in tree.tree_structure("eiche"):
            self.relative[d_pos-(0,1,0)] = block

    def get_tags(self):
        return super(Setzling,self).get_tags().union({"random_tick"}) - {"solid"}

    def collides_with(self,area):
        return False
