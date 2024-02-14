from resources import *
import tree

@register_block("DIRT")

class Dirt(Block):
    blast_resistance = 0
    def handle_event_random_tick(self,events):
        if self.world.blocks[self.position + (0,1,0)] == "AIR":
            self.turn_into("GRASS")
            return True
        return False

    def get_tags(self):
        return super().get_tags() | {"random_tick"}

@register_block("GRASS")
class Grassblock(Block):
    def handle_event_random_tick(self,events):
        block_above = self.relative[(0,1,0)]
        if block_above == "AIR":
            if random.random()<0.008:
                flower_block = random.choice(["grass","grass","grass","grass","HALM","HALM","HALM","HALM",
                                              "LilaBlume","WeisseBlume","RoteBlume",
                                              "BlaueBlume","GelbeBlume","SonnenBlume"])
                self.world.request_set_block(block_above.position, flower_block)
        elif block_above not in ["AIR","grass","LilaBlume","WeisseBlume","RoteBlume","BlaueBlume","GelbeBlume","SonnenBlume","HALM","Fence"]:
            self.turn_into("DIRT")
            return True
        return False
    def get_tags(self):
        return super().get_tags() | {"random_tick"}
            

@register_block("grass")
@register_block("LilaBlume")
@register_block("WeisseBlume")
@register_block("BlaueBlume")
@register_block("RoteBlume")
@register_block("GelbeBlume")
@register_block("SonnenBlume")
@register_block("HALM")
class Plant(Block):
    #def collides_with(self,area):
    #    return False
    def handle_event_block_update(self,events):
        if self.relative[(0,-1,0)] != "GRASS":
            self.turn_into("AIR")
            return True
        return False
    def get_tags(self):
        return (super().get_tags() - {"solid"}) | {"block_update"}


@register_block("Setzling")

class Setzling(Block):
    blast_resistance = 0
    def handle_event_random_tick(self,events):
        for d_pos, block in tree.tree_structure("eiche"):
            replace_block = self.relative[(d_pos[0], d_pos[1]-1, d_pos[2])]
            self.world.request_set_block(replace_block.position, block)
        return False

    def get_tags(self):
        return (super().get_tags() - {"solid"}) | {"random_tick"}

    #def collides_with(self,area):
    #    return False
