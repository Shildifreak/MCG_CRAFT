from mcgcraft import Block, register_block

@register_block("TORCH")
class Torch(Block):
    def block_update(self,directions):
        a = 0
        for direction in directions:
            block = self.world[self.position+direction]
            if block["powered"]:
                self["powered"] = 0
                self["powering"] = ()
                a += 1
        if a == 0:
            self["powered"] = 15
            self["powering"] = ((0,1,0),)
    def collides_with(self,hitbox,position):
        return False
    
