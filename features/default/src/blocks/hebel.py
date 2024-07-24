from resources import *


class HEBEL(Block):
    defaults = Block.defaults.copy()
    defaults["p_ambient"] = True
    defaults["p_level"] = -15
    def clicked(self,character,face,item):
        self["rotation"] = (self["rotation"] + 2) % 4
        face = FACES["tbsnwe".find(self["base"])]
        self["p_directions"] = (face,)
        if self["p_level"] > 0:
            self["p_level"] = -15
        else:
            self["p_level"] = 15
        self.save()
