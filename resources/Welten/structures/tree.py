import random
def tree_structure(baumtyp):
    baumstruktur = random.randint(1,2)
    if baumtyp == "eiche":
        if baumstruktur == 1:
            height = 3
            for y in range(1,height+1):
                yield (0,y,0), "HOLZ"
            for x in range(-2,3):
                for z in range(-2,3):
                        yield (x,1+height,z), "LAUB"
            for x in range(-1,2):
                for z in range(-1,2):
                    yield (x,y+height-1,z), "LAUB"
        elif baumstruktur == 2:
            height = 5
            for y in range(1,height):
                yield (0,y,0), "HOLZ"
            for x in range(-2,3):
                for z in range(-2,3):
                    for y in range(2):
                        yield (x,y+height,z), "LAUB"
            for x in range(-1,2):
                for z in range(-1,2):
                    yield (x,y+height+1,z), "LAUB"
            
            #if 0 <= y-chunkpos[1] < chunksize
