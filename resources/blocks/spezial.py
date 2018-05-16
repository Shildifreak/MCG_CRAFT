from base import *


@register_block("WAND")

class Wand(Block):
    def collides_with(self,entity):
        return False
