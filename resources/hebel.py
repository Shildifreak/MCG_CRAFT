from base import *

@register_block("HEBEL")
class HebelBlock(Block):
    def activated(self,character,face):
        block = self.world[self.position]
        block["rotation"] += 2
        block["rotation"] %= 4
