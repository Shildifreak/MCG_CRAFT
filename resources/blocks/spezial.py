from mcgcraft import Block, register_block


@register_block("WAND")

class Wand(Block):
    def collides_with(self,entity):
        return False
