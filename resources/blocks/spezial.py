from resources import *


@register_block("WAND")

class Wand(Block):
    def collides_with(self,area):
        return False

    def get_tags(self):
        return super(Wand,self).get_tags() - {"solid"}
