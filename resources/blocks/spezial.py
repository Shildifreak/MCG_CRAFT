from mcgcraft import Block, register_block


@register_block("WAND")

class Wand(Block):
    def collides_with(self,hitbox,position):
        return False
