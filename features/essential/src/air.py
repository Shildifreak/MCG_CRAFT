from resources import *

class AIR(Block):
    def get_tags(self):
        return set() # no solid tag, no explosion tag
    def collides_with(self,area):
        return False
