from resources import *


@register_block("AIR")
class AirBlock(Block):
    def get_tags(self):
        return set() # no solid tag, no explosion tag
    def collides_with(self,area):
        return False
