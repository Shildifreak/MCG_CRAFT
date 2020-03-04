import house
def init(welt):
    for dpos,block in house.house_structure(39,4):
        welt.blocks[dpos] = block

spawnpoint = (0,10,0)
