import random
import tree
terrain_generator = []
spawnpoint = (50,70,50)

def init(welt):
    n = 100
    bergh = random.randint(5,15)
    w = [[0 for i in range(n)] for i in range(n)]#Weltkarte, physisch
    berge = []#zu bauende Berge
    ds = 1
    for i in range(10*n):
        berge.append((random.randint(0,n-1),random.randint(0,n-1)))
    for berg in berge:
        w[berg[0]][berg[1]] = 1
    while berge:
        for berg in berge:
            for dx in range(-ds,ds+1):
                for dy in range(-ds,ds+1):
                    if berg[0]+dx >= 0 and berg[0]+dx < n and berg[1]+dy >= 0 and berg[1]+dy < n:
                        w[berg[0]+dx][berg[1]+dy]+=1
        ds+=1
        for i in range(random.randint(int(n/10),n)):
            if berge:
                berge.pop(random.randint(0,len(berge)-1))
    
    
    for x in range(0,n):
        for z in range(0,n):
            h = int(w[x][z]/bergh)
            welt.blocks[(x,-6,z)] = "BEDROCK"
            for y in range(-5,h):
                welt.blocks[(x,y,z)] = "STONE"
            for y in range(h,h+3):
                welt.blocks[(x,y,z)] = "DIRT"
            welt.blocks[(x,h+3,z)] = "GRASS"
            if random.random()<0.005:
                for _ in range(5):
                    for d_pos, block in tree.tree_structure("eiche"):
                        dx, dy, dz = d_pos
                        welt.blocks[(x+dx,h+3+dy,z+dz)] = block
    
