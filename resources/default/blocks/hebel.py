from resources import *

@register_block("HEBEL")
class HebelBlock(Block):
    defaults = Block.defaults.copy()
    defaults["p_ambient"] = True
    def activated(self,character,face):
        self["rotation"] = (self["rotation"] + 2) % 4
        face = FACES["tbsnwe".find(self["base"])]
        self["p_directions"] = (face,)
        if self["p_level"]:
            self["p_level"] = 0
        else:
            self["p_level"] = 15
        self.save()
