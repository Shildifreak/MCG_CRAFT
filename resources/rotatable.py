from base import *

@register_item("HERZ")
@register_item("GESICHT")
class RotatableBlockItem(Item):
    def use_on_block(self,character,blockpos,face):
        new_pos = blockpos + face
        block_id = self.item["id"]
        faces = {( 0, 1, 0):"t",
                 ( 0,-1, 0):"b",
                 ( 0, 0, 1):"s",
                 ( 0, 0,-1):"n",
                 ( 1, 0, 0):"e",
                 (-1, 0, 0):"w",
                 }
        base = faces.get(tuple(map(int,face*-1)),"")
        if base == "b":
            r = int((character["rotation"][0] - 45) // 90) % 4
        else:
            r = 0
        print base, r
        character.world[new_pos] = block_id + ":%i%s" % (r, base)

@register_block("GESICHT")
class RotatableBlock(Block):
    def activated(self,character,face):
        block = self.world[self.position]
        key, state = block.rsplit(":",1)
        state = state.replace("3","4")
        state = state.replace("2","3")
        state = state.replace("1","2")
        state = state.replace("0","1")
        state = state.replace("4","0")
        self.world[self.position] = key+":"+state
