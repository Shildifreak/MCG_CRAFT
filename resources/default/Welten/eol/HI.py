def init(welt):
    n = 100
    for x in range (-n,n):
        for y in range (-n,n):
            welt.blocks[(x,0,y)] = "DIAMANT"

spawnpoint = (0,5,0)
