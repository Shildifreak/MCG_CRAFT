# -*- coding: cp1252 -*-
import random
def Wuste(self):
      n = 200 # 1/2 width and height of world
      s = 1  # step size
      y = 0  # initial y height
      
      for x in xrange(-n, n + 1, s):
           for z in xrange(-n, n + 1, s):
               self.add_block((x, y - 2, z), "Sand", immediate=False)
               self.add_block((x, y - 3, z), "Sand", immediate=False)
               self.add_block((x, y - 4, z), "Sand", immediate=False)
               self.add_block((x, y - 5, z), "Sandstein", immediate=False)
               self.add_block((x, y - 6, z), "Sandstein", immediate=False)
               self.add_block((x, y - 7, z), "Stein", immediate=False)
               self.add_block((x, y - 8, z), "Stein", immediate=False)
               self.add_block((x, y - 9, z), "Stein", immediate=False)
               self.add_block((x, y - 10, z), "Stein", immediate=False)
               self.add_block((x, y - 11, z), "Grundgestein", immediate=False)
               if x in (-n, n) or z in (-n, n):
                   # create outer walls.
                   for dy in xrange(-13, 3):
                       self.add_block((x, y + dy, z), "Grundgestein", immediate=False)
                        
           
      o = n - 8
      for N_ in xrange(10):
            a = random.randint(-o, o)  # x position of the hill
            b = random.randint(-o, o)  # z position of the hill
            c = -1  # base of the hill
            h = random.randint(3, 6)  # height of the hill
            s = random.randint(4, 8)  # 2 * s is the side length of the hill
            d = 1  # how quickly to taper off the hills
            t = random.choice(["Sand","Sandstein"])
            for y in xrange(c, c + h):
                for x in xrange(a - s, a + s + 1):
                    for z in xrange(b - s, b + s + 1):
                        if (x - a) ** 2 + (z - b) ** 2 > (s + 1) ** 2:
                            continue
                        if (x - 0) ** 2 + (z - 0) ** 2 < 5 ** 2:
                            continue
                        self.add_block((x, y, z), t, immediate=False)
                s -= d # decrement side lenth so hills taper off
