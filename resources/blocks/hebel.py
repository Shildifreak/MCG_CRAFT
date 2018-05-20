from resources import *

@register_block("HEBEL")
class HebelBlock(Block):
    def block_update(self,directions):
        pass
    def activated(self,character,face):
        self["rotation"] += 2
        self["rotation"] %= 4
        face = FACES["tbsnwe".find(self["base"])]
        self["p_directions"] = (face,)
        if self["p_level"]:
            self["p_level"] = 0
        else:
            self["p_level"] = 15
