from resources import *

@register_item("HERZ")
@register_item("GESICHT")
@register_item("HEBEL")
@register_item("FAN")
@register_item("TORCH")
@register_item("HOLZ")
@register_item("Repeater")
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
            r = int(( character["rotation"][0] + 45) // 90) % 4
        elif base == "t":
            r = int((-character["rotation"][0] + 45) // 90) % 4            
        else:
            r = 0
        block = {"id":block_id,"rotation":r,"base":base}
        character.world[new_pos] = block

@register_block("GESICHT")
class RotatableBlock(Block):
    def activated(self,character,face):
        block = self.world[self.position]
        block["rotation"] += 1
        block["rotation"] %= 4
