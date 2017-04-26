# -*- coding: cp1252 -*-
import random
def Grassland(self):
        n = 50 # 1/2 width and height of world
        s = 1  # step size
        y = 0  # initial y height
        
        for x in xrange(-n, n + 1, s):
            for z in xrange(-n, n + 1, s):
                self.add_block((x, y - 2, z), "Grass", immediate=False)
                self.add_block((x, y - 3, z), "Dirt", immediate=False)
                self.add_block((x, y - 4, z), "Dirt", immediate=False)
                self.add_block((x, y - 5, z), "Dirt", immediate=False)
                self.add_block((x, y - 6, z), "Stein", immediate=False)
                self.add_block((x, y - 7, z), "Stein", immediate=False)
                self.add_block((x, y - 8, z), "Stein", immediate=False)
                self.add_block((x, y - 9, z), "Stein", immediate=False)
                self.add_block((x, y - 10, z), "Stein", immediate=False)
                self.add_block((x, y - 11, z), "Grundgestein", immediate=False)
                if x in (-n, n) or z in (-n, n):
                    # create outer walls.
                    for dy in xrange(-11, 3):
                        self.add_block((x, y + dy, z), "Grundgestein", immediate=False)

        # generate the hills randomly
        o = n - 10
        for _ in xrange(1):
            a = random.randint(-o, o)  # x position of the hill
            b = random.randint(-o, o)  # z position of the hill
            c = -1  # base of the hill
            h = random.randint(3, 6)  # height of the hill
            s = random.randint(4, 8)  # 2 * s is the side length of the hill
            d = 1  # how quickly to taper off the hills
            t = random.choice(["Grass"])
            for y in xrange(c, c + h):
                for x in xrange(a - s, a + s + 1):
                    for z in xrange(b - s, b + s + 1):
                        if (x - a) ** 2 + (z - b) ** 2 > (s + 1) ** 2:
                            continue
                        if (x - 0) ** 2 + (z - 0) ** 2 < 5 ** 2:
                            continue
                        self.add_block((x, y, z), t, immediate=False)
                s -= d  # decrement side lenth so hills taper off
        
         #kreirt die Baume automatisch
        o = n - 10
        for b_ in xrange(1):
            x = random.randint(-o, o)  # x position des Baumes 
            z = random.randint(-o, o)  # z position des Baumes
            y = -1  # Basis des Baums
            while(x,y,z) in self.world:
                y += 1
            for i in range(random.randint(3,4)):
                self.add_block((x, y, z), "Eichenholz", immediate=False)
                y += 1
            a = x
            b = z
            c = y
            h = random.randint(2, 3)  # seite des Baums 
            s = random.randint(4, 6)  # seite des baume
            d = 1   
            t = "Laub"
            for y in xrange(c, c + h):
                for x in xrange(a - s, a + s + 1):
                    for z in xrange(b - s, b + s + 1):
                        if (x - a) ** 2 + (z - b) ** 2 > (s + 1) ** 2:
                            continue
                        if (x - 0) ** 2 + (z - 0) ** 2 < 5 ** 2:
                            continue
                        self.add_block((x, y, z), t, immediate=False)
                s -= d
        o = n - 10
        
        for b_ in xrange(1):
            x = random.randint(-o, o)  # x position des Baumes 
            z = random.randint(-o, o)  # z position des Baumes
            y = -1  # Basis des Baums
            while(x,y,z) in self.world:
                y += 1
            for i in range(random.randint(3,4)):
                self.add_block((x, y, z), "Birkenholz", immediate=False)
                y += 1
            a = x
            b = z
            c = y
            h = random.randint(2, 3)  # seite des Baums 
            s = random.randint(3, 4)  # seite des baume
            d = 1   
            t = "Laub"
            for y in xrange(c, c + h):
                for x in xrange(a - s, a + s + 1):
                    for z in xrange(b - s, b + s + 1):
                        if (x - a) ** 2 + (z - b) ** 2 > (s + 1) ** 2:
                            continue
                        if (x - 0) ** 2 + (z - 0) ** 2 < 5 ** 2:
                            continue
                        self.add_block((x, y, z), t, immediate=False)
                s -= d
        o = n - 10
        for b_ in xrange(1):
            x = random.randint(-o, o)  # x position des Baumes 
            z = random.randint(-o, o)  # z position des Baumes
            y = -1  # Basis des Baums
            while(x,y,z) in self.world:
                y += 1
            for i in range(random.randint(3,4)):
                self.add_block((x, y, z), "Akazienholz", immediate=False)
                y += 1
            a = x
            b = z
            c = y
            h = random.randint(2, 3)  # seite des Baums 
            s = random.randint(3, 4)  # seite des baume
            d = 1   
            t = "Laub"
            for y in xrange(c, c + h):
                for x in xrange(a - s, a + s + 1):
                    for z in xrange(b - s, b + s + 1):
                        if (x - a) ** 2 + (z - b) ** 2 > (s + 1) ** 2:
                            continue
                        if (x - 0) ** 2 + (z - 0) ** 2 < 5 ** 2:
                            continue
                        self.add_block((x, y, z), t, immediate=False)
                s -= d
        o = n - 10

        #Generiert Haus
        for n_ in xrange(1):
            x = random.randint(5,5) # x position Haus
            z = random.randint(5,5) # z position Haus
            y = -2  #Basis Haus
            for N_ in range(6):
                z += 1
                self.add_block((x,y,z),"Eichenholz")
            for N_ in range(9):
                x += 1
                self.add_block((x,y,z),"Eichenholz")
            
            for N_ in  range(6):
                z -= 1
                self.add_block((x,y,z),"Eichenholz")
                for N_ in range(9):
                    x -= 1
                    self.add_block((x,y,z),"Eichenholz")
                for N_ in range(9):
                    x += 1
                    self.add_block((x,y,z),"Eichenholz")
            # bis hier Platform Haus
            for N_ in range(2):
                y += 1
                for N_ in range(1):
                    self.add_block((x,y,z),"Eichenbretter")
                for N_ in range(6):
                    z += 1
                    self.add_block((x,y,z),"Eichenbretter")
                for N_ in range(9):
                    x -= 1
                    self.add_block((x,y,z),"Eichenbretter")
                for N_ in range(6):
                    z -= 1
                    self.add_block((x,y,z),"Eichenbretter")
                for N_ in range(3):
                    x += 1
                    self.add_block((x,y,z),"Eichenbretter")
                x += 1
                for N_ in range(5):
                    x += 1
                    self.add_block((x,y,z),"Eichenbretter")
            y += 1
            for N_ in range(1):
                self.add_block((x,y,z),"Eichenbretter")
            for N_ in range(6):
                z += 1
                self.add_block((x,y,z),"Eichenbretter")
            for N_ in range(9):
                x -= 1
                self.add_block((x,y,z),"Eichenbretter")
            for N_ in range(6):
                z -= 1
                self.add_block((x,y,z),"Eichenbretter")
            for N_ in range(9):
                x += 1
                self.add_block((x,y,z),"Eichenbretter")
            # bis hier Wände von Haus
            y -= 2
            x -= 2
            z += 1
            self.add_block((x,y,z),"Ofen2")
            x += 1
            self.add_block((x,y,z),"Werkbank")
            x -= 7
            for N_ in range(5):
                self.add_block((x,y,z),"Bucherregal")
                z += 1
            y += 1
            z -= 1
            for N_ in range(5):
                self.add_block((x,y,z),"Bucherregal")
                z -= 1
            y += 1
            z += 1
            for N_ in range(5):
                self.add_block((x,y,z),"Bucherregal")
                z += 1
            y += 1
            z -= 1
            for N_ in range(8):
                self.add_block((x,y,z),"Eichenbretter")
                x += 1
            x -= 1
            z -= 1
            for N_ in range(8):
                self.add_block((x,y,z),"Eichenbretter")
                x -= 1
            x += 1
            z -= 1
            for N_ in range(8):
                self.add_block((x,y,z),"Eichenbretter")
                x += 1
            x -= 1
            z -= 1
            for N_ in range(8):
                self.add_block((x,y,z),"Eichenbretter")
                x -= 1
            x += 1
            z -= 1
            for N_ in range(8):
                self.add_block((x,y,z),"Eichenbretter")
                x += 1
