import random 

terrain_generator = []
spawnpoint = (0,20,0)

def init(welt):
        """ Initialize the world by placing all the blocks.

        """
        n = 50  # 1/2 width and height of world
        s = 1  # step size
        y = 0 # initial y height
        
        for x in xrange(-n, n + 1, s):
            for z in xrange(-n, n + 1, s):
                # create a layer stone an grass everywhere.
                welt[x, y - 2, z]= "SCHNEEERDE"
                welt[x, y - 3, z]= "DIRT"
                welt[x, y - 4, z]= "DIRT"
                welt[x, y - 5, z]= "DIRT"
                welt[x, y - 6, z]= "STONE"
                welt[x, y - 7, z]= "STONE"
                welt[x, y - 8, z]= "STONE"
                welt[x, y - 9, z]= "STONE"
                welt[x, y - 10, z]= "STONE"
                welt[x, y - 11, z]= "STONE"
                welt[x, y - 12, z]= "STONE"
                welt[x, y - 13, z]= "BEDROCK"
                if x in (-n, n) or z in (-n, n):
                    # create outer walls.
                    for dy in xrange(-11, 3):
                        welt[x, y + dy, z]= "BEDROCK"

        # generate the hills randomly
        o = n - 10
        for _ in xrange(10):
            a = random.randint(-o, o)  # x position of the hill
            b = random.randint(-o, o)  # z position of the hill
            c = -1  # base of the hill
            h = random.randint(3, 6)  # height of the hill
            s = random.randint(4, 8)  # 2 * s is the side length of the hill
            d = 1  # how quickly to taper off the hills
            t = random.choice(["SCHNEEERDE","SCHNEE","WOLLE"])
            for y in xrange(c, c + h):
                for x in xrange(a - s, a + s + 1):
                    for z in xrange(b - s, b + s + 1):
                        if (x - a) ** 2 + (z - b) ** 2 > (s + 1) ** 2:
                            continue
                        if (x - 0) ** 2 + (z - 0) ** 2 < 5 ** 2:
                            continue
                        welt[x, y, z]=t
                s -= d  # decrement side lenth so hills taper off
