# -*- coding: cp1252 -*-
import random
import tree
def init(welt):
        n = 50 # 1/2 width and height of world
        s = 1  # step size
        y = 0  # initial y height
        
        for x in range(-n, n + 1, s):
            for z in range(-n, n + 1, s):
                welt.blocks[(x,y-2,z)] = "GRASS"
                welt.blocks[(x,y-3,z)] = "DIRT"
                welt.blocks[(x,y-4,z)] = "DIRT"
                welt.blocks[(x,y-5,z)] = "DIRT"
                welt.blocks[(x, y - 6,z)] = "STONE"
                welt.blocks[(x, y - 7, z)] = "STONE"
                welt.blocks[(x, y - 8, z)] = "STONE"
                welt.blocks[(x, y - 9, z)] = "STONE"
                welt.blocks[(x, y - 10, z)] = "STONE"
                welt.blocks[(x, y - 11, z)] = "BEDROCK"
                if x in (-n, n) or z in (-n, n):
                    # create outer walls.
                    for dy in range(-11, 3):
                        welt.blocks[(x, y + dy, z)] = "BEDROCK"
        for _ in range(35):
            x = random.randint(-n+5,n-5)
            y = -2
            z = random.randint(-n+5,n-5)
            for d_pos, block in tree.tree_structure("eiche"):
                dx, dy, dz = d_pos
                welt.blocks[(x+dx,y+dy,z+dz)] = block
                        

spawnpoint = (0,5,0)
