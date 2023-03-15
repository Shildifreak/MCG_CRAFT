from resources import *

@register_block("HEBEL")
class HebelBlock(Block):
    defaults = Block.defaults.copy()
    defaults["p_ambient"] = True
    defaults["p_level"] = -15
    def activated(self,character,face):
        self["rotation"] = (self["rotation"] + 2) % 4
        face = FACES["tbsnwe".find(self["base"])]
        self["p_directions"] = (face,)
        if self["p_level"] > 0:
            self["p_level"] = -15
        else:
            self["p_level"] = 15
        self.save()
