import random
def Crazyworld(self):
        n = 50  # 1/2 width and height of world
        s = 1  # step size
        y = 0 # initial y height
        
        for x in xrange(-n, n + 1, s):
            for z in xrange(-n, n + 1, s):
                # create a layer stone an grass everywhere.
                self.add_block((x, y - 2, z), "Schildblock", immediate=False)
                self.add_block((x, y - 3, z), "Diamant", immediate=False)
                self.add_block((x, y - 4, z), "Schneeerde", immediate=False)
                self.add_block((x, y - 5, z), "Grundgestein", immediate=False)
                self.add_block((x, y - 6, z), "Stein", immediate=False)
                self.add_block((x, y - 7, z), "Laub", immediate=False)
                self.add_block((x, y - 8, z), "Eichenholz", immediate=False)
                self.add_block((x, y - 9, z), "Green", immediate=False)
                self.add_block((x, y - 10, z), "Hellblau", immediate=False)
                self.add_block((x, y - 11, z), "Rot", immediate=False)
                self.add_block((x, y - 12, z), "Wolle", immediate=False)
                self.add_block((x, y - 13, z), "Grass", immediate=False)
                if x in (-n, n) or z in (-n, n):
                    # create outer walls.
                    for dy in xrange(-11, 3):
                        self.add_block((x, y + dy, z), "Gold", immediate=False)

        # generate the hills randomly
        o = n - 10
        for _ in xrange(10):
            a = random.randint(-o, o)  # x position of the hill
            b = random.randint(-o, o)  # z position of the hill
            c = -1  # base of the hill
            h = random.randint(3, 6)  # height of the hill
            s = random.randint(4, 8)  # 2 * s is the side length of the hill
            d = 1  # how quickly to taper off the hills
            t = random.choice(["Schildblock", "Eichenbretter", "Iron", "Diamant", "Sand", "Schneeerde", "Gold", "Stein","Grundgestein"])
            for y in xrange(c, c + h):
                for x in xrange(a - s, a + s + 1):
                    for z in xrange(b - s, b + s + 1):
                        if (x - a) ** 2 + (z - b) ** 2 > (s + 1) ** 2:
                            continue
                        if (x - 0) ** 2 + (z - 0) ** 2 < 5 ** 2:
                            continue
                        self.add_block((x, y, z), t, immediate=False)
                s -= d  # decrement side lenth so hills taper off
