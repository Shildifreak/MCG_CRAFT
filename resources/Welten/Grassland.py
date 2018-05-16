# -*- coding: cp1252 -*-
import random
import tree
def init(welt):
        n = 50 # 1/2 width and height of world
        s = 1  # step size
        y = 0  # initial y height
        
        for x in xrange(-n, n + 1, s):
            for z in xrange(-n, n + 1, s):
                welt[(x,y-2,z)] = "GRASS"
                welt[(x,y-3,z)] = "DIRT"
                welt[(x,y-4,z)] = "DIRT"
                welt[(x,y-5,z)] = "DIRT"
                welt[(x, y - 6,z)] = "STONE"
                welt[(x, y - 7, z)] = "STONE"
                welt[(x, y - 8, z)] = "STONE"
                welt[(x, y - 9, z)] = "STONE"
                welt[(x, y - 10, z)] = "STONE"
                welt[(x, y - 11, z)] = "BEDROCK"
                if x in (-n, n) or z in (-n, n):
                    # create outer walls.
                    for dy in xrange(-11, 3):
                        welt[(x, y + dy, z)] = "BEDROCK"
        for n in range(5):
            x = random.randint(-11,20)
            y = -2
            z = random.randint(-11,20)
            for d_pos, block in tree.tree_structure("eiche"):
                dx, dy, dz = d_pos
                welt[(x+dx,y+dy,z+dz)] = block
                        

terrain_generator = []

spawnpoint = (0,5,0)
