from base import *

@register_block("HEBEL")
class HebelBlock(Block):
    def activated(self,character,face):
        self["rotation"] += 2
        self["rotation"] %= 4
        if self["powered"]:
            self["powered"] = 0
        else:
            self["powered"] = 15
