import house
def init(welt):
    for dpos,block in house.house_structure(6,7):
        welt.blocks[dpos] = block

spawnpoint = (0,10,0)
