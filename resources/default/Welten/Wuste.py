import random

spawnpoint = (0,20,0)

def init(welt):
      n = 50 # 1/2 width and height of world
      s = 1  # step size
      y = 0  # initial y height
      
      for x in range(-n, n + 1, s):
           for z in range(-n, n + 1, s):
               welt.blocks[x, y - 2, z]="SAND"
               welt.blocks[x, y - 3, z]= "SAND"
               welt.blocks[x, y - 4, z]= "SAND"
               welt.blocks[x, y - 5, z]= "HOLZ"
               welt.blocks[x, y - 6, z]= "HOLZ"
               welt.blocks[x, y - 7, z]= "STONE"
               welt.blocks[x, y - 8, z]= "STONE"
               welt.blocks[x, y - 9, z]= "STONE"
               welt.blocks[x, y - 10, z]= "STONE"
               welt.blocks[x, y - 11, z]= "BEDROCK"
               if x in (-n, n) or z in (-n, n):
                   # create outer walls.
                   for dy in range(-13, 3):
                       welt.blocks[x, y + dy, z]= "BEDROCK"
                        
           
      o = n - 8
      for N_ in range(10):
            a = random.randint(-o, o)  # x position of the hill
            b = random.randint(-o, o)  # z position of the hill
            c = -1  # base of the hill
            h = random.randint(3, 6)  # height of the hill
            s = random.randint(4, 8)  # 2 * s is the side length of the hill
            d = 1  # how quickly to taper off the hills
            t = random.choice(["SAND","HELLORANGE"])
            for y in range(c, c + h):
                for x in range(a - s, a + s + 1):
                    for z in range(b - s, b + s + 1):
                        if (x - a) ** 2 + (z - b) ** 2 > (s + 1) ** 2:
                            continue
                        if (x - 0) ** 2 + (z - 0) ** 2 < 5 ** 2:
                            continue
                        welt.blocks[x, y, z]= t
                s -= d # decrement side lenth so hills taper off
