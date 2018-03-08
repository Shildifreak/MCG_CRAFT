import random
def tree_structure(baumtyp):
    baumstruktur = random.randint(1)
    if baumtyp == "eiche":
        if baumstrucktur == 1:
            height = 3
            for y in range(1,height):
                yield (0,y,0), "HOLZ"
            for x in range(-1,2):
                for z in range(-1,2):
                    for y in range(3):
                        yield (x,y+height,z), "LAUB"
            #if 0 <= y-chunkpos[1] < chunksize:

