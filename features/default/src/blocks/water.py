from resources import *


class WATER(Block):
    def get_tags(self):
        return (super().get_tags() - {"solid"}) | {"water"}

    def collides_with(self, area):
        return False
