from resources import *

@register_item("Stick1")
@register_item("Stick2")
@register_item("Stick3")
@register_item("Arrow")
class Material(Item):
    def use_on_block(self, character, blockpos, face):
        pass
