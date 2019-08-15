import random

spawnpoint = (0,20,0)

def init(welt):
    """ Initialize the world by placing all the blocks.

    """
    n = 50  # 1/2 width and height of world
    s = 1  # step size
    y = 0 # initial y height

    for _ in range(100):
        a = random.randint(-n, n)
        b = random.randint(-n, n)
        welt.blocks[(a, y -1, b)] = "TNT"
    for x in range(-n, n + 1, s):
        for z in range(-n, n + 1, s):
            # create a layer stone an grass everywhere.
            welt.blocks[(x, y -  2, z)] = "GRUN"
            welt.blocks[(x, y -  3, z)] = "BRAUN"
            welt.blocks[(x, y -  4, z)] = "BRAUN"
            welt.blocks[(x, y -  5, z)] = "BRAUN"
            welt.blocks[(x, y -  6, z)] = "GRAU"
            welt.blocks[(x, y -  7, z)] = "GRAU"
            welt.blocks[(x, y -  8, z)] = "GRAU"
            welt.blocks[(x, y -  9, z)] = "GRAU"
            welt.blocks[(x, y - 10, z)] = "GRAU"
            welt.blocks[(x, y - 11, z)] = "GRAU"
            welt.blocks[(x, y - 12, z)] = "GRAU"
            welt.blocks[(x, y - 13, z)] = "STONE"
            if x in (-n, n) or z in (-n, n):
                # create outer walls.
                for dy in range(-13, 3):
                    welt.blocks[(x, y + dy, z)] = "STONE"

        # generate the hills randomly
        o = n - 10
    for _ in range(10):
        a = random.randint(-o, o)  # x position of the hill
        b = random.randint(-o, o)  # z position of the hill
        c = -1  # base of the hill
        h = random.randint(3, 6)  # height of the hill
        s = random.randint(4, 8)  # 2 * s is the side length of the hill
        d = 1  # how quickly to taper off the hills
        t = random.choice(["HELLBLAU", "BRAUN", "GRAU", "ROT"])
        for y in range(c, c + h):
            for x in range(a - s, a + s + 1):
                for z in range(b - s, b + s + 1):
                    if (x - a) ** 2 + (z - b) ** 2 > (s + 1) ** 2:
                       continue
                    if (x - 0) ** 2 + (z - 0) ** 2 < 5 ** 2:
                        continue
                    welt.blocks[(x, y, z)] = t
            s -= d  # decrement side lenth so hills taper off
     #kreirt die Baume automatisch
    o = n - 10
    for b_ in range(5):
        x = random.randint(-o, o)  # x position des Baumes
        z = random.randint(-o, o)  # z position des Baumes
        y = -1  # Basis des Baums
        while welt.blocks[(x,y,z)] != "AIR":
            y += 1
        for i in range(random.randint(3,4)):
            welt.blocks[(x, y, z)] = "BRAUN"
            y += 1
            a = x
            b = z
            c = y
            h = random.randint(2, 3)  # seite des Baums 
            s = random.randint(4, 6)  # seite des baume
            d = 1   
            for y in range(c, c + h):
                for x in range(a - s, a + s + 1):
                    for z in range(b - s, b + s + 1):
                        if (x - a) ** 2 + (z - b) ** 2 > (s + 1) ** 2:
                            continue
                        if (x - 0) ** 2 + (z - 0) ** 2 < 5 ** 2:
                            continue
                        welt.blocks[(x, y, z)] = "HELLGRUN"
                s -= d  
