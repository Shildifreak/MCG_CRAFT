from resources import *

@register_item("STONESLAB")
@register_item("HERZ")
@register_item("GESICHT")
@register_item("HEBEL")
@register_item("Button")
@register_item("FAN")
@register_item("TORCH")
@register_item("HOLZ")
@register_item("Repeater")
@register_item("ROCKET")
class RotatableBlockItem(Item):
    def block_version_on_place(self,character,block,face):
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
        return {"id":block_id,"rotation":r,"base":base}

@register_block("GESICHT")
class RotatableBlock(Block):
    def clicked(self,character,face,item):
        self["rotation"] += 1
        self["rotation"] %= 4
        self.save()
