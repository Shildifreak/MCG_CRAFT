def tree_structure(height):
    #if 0 <= y-chunkpos[1] < chunksize:
    for y in range(1,height):
        yield (0,y,0), "HOLZ"
    for x in range(-1,2):
        for z in range(-1,2):
            for y in range(3):
                yield (x,y+height,z), "LAUB"
