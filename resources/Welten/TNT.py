import random

def init(welt):
    n=50
    y = 0
    
    for x in xrange(-n, n + 1 ):
        for z in xrange(-n, n + 1):
            welt[(x,y-2,z)] = "GRASS"
            welt[(x,y-3,z)] = "DIRT"
            welt[(x,y-4,z)] = "DIRT"
            welt[(x,y-5,z)] = "DIRT"
            welt[(x, y - 6,z)] = "STONE"
            welt[(x, y - 7, z)] = "STONE"
            welt[(x, y - 8, z)] = "STONE"
            welt[(x, y - 9, z)] = "STONE"
            welt[(x, y - 10, z)] = "STONE"
            welt[(x, y - 11, z)] = "STONE"
            welt[(x, y - 12, z)] = "STONE"
            welt[(x, y - 13, z)] = "STONE"
            welt[(x, y - 14, z)] = "STONE"
            welt[(x, y - 15, z)] = "STONE"
            welt[(x, y - 16, z)] = "STONE"
            welt[(x, y - 17, z)] = "STONE"
            welt[(x, y - 18, z)] = "STONE"
            welt[(x, y - 19, z)] = "STONE"
            welt[(x, y - 20, z)] = "BEDROCK"
            if x in (-n, n) or z in (-n, n):
                # create outer walls.
                for dy in xrange(-11, 3):
                    welt[(x, y + dy, z)] = "BEDROCK"
    for n in range(50):
        x = random.randint(-n-1,n)
        z = random.randint(-n-1,n)
        t = random.choice(["A-TNT","TNT","Setzling","B-TNT",])

        welt[(x,y-1,z)]= t
spawnpoint = (0,7,0)
terrain_generator = []
