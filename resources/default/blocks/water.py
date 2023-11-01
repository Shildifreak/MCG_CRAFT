from resources import *


@register_block("WATER")
class WaterBlock(Block):
    def get_tags(self):
        return (super().get_tags() - {"solid"}) | {"water"}
