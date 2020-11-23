import collections
import random
import functools

import tree

def init(welt):
    pass

@functools.lru_cached(1000)
def terrain(position):
    x,y,z = position

    # if baum:
    #   return baum
    if y <= steinhoehe(x,z):
        return "STONE"
    if y <= erdhoehe(x,z):
        return "DIRT"
    if y <= grashoehe(x,z):
        return "GRASS"
    return "AIR"

def cache(func):
    c = collections.OrderedDict()
    def cached_func(*args,**kwargs):
        key = (args,frozenset(kwargs.items()))
        try:
            return c[key]
        except:
            ret = func(*args,**kwargs)
            c[key] = ret
            if len(c) > 100:
                c.popitem(False)
            return ret
    return cached_func

def f(x,z,m):
    ax = 2*abs(x)+(x>0)+100
    az = abs(z)+10#2*abs(z)+(z>0)
    d = ax+1+ax//(m-1)
    y1 = (7**az+1)%(d)%m
    return y1

def g(x,z,m=5):
    random.seed(2*abs(x)+(x<0))
    r = random.random()
    random.seed(z+r)
    y = random.random()
    return int(y*m)

f = g

@cache
def f2(x,z):
    return (f(x,z,7)+f(z,x,11))%7-3.5

#def f2(x,z):
#    return (x+z)%2

def f3(x,z,s=10):
    x1 = x//s
    x2 = x1+1
    z1 = z//s
    z2 = z1+1
    y11 = f2(x1,z1)
    y12 = f2(x1,z2)
    y21 = f2(x2,z1)
    y22 = f2(x2,z2)
    dx = (x%s)/(1.0*s)
    dz = (z%s)/(1.0*s)
    p11 = min((1-dx),(1-dz))
    p12 = min((1-dx),   dz )
    p21 = min(   dx ,(1-dz))
    p22 = min(   dx ,   dz )
    return y11*p11+y22*p22+y12*p12+y21*p21

def f4(x,z):
    y = 0
    y += 2*f3(x,z,9)
    y += 2.5*f3(x,z,20)
    y += 3.5*f3(x,z,50)
    return sum((n**0.3)*f3(x,z,n) for n in (9,20,50))

def f5(x,z,sealevel=-5):
    y = f4(x,z)
    return y if y>sealevel else sealevel

if __name__ == "__main__":
    from display3d import display
    display(f5,80)


heightfunction = f4


def terrain_generator_from_heightfunc(heightfunc,block_name):
    """heightfunc(int,int)->int is used to create generator function
    (can be used as decorator)"""
    def terrain_generator(chunk):
        x,y,z = chunk.position<<chunk.chunksize
        c = 1 << chunk.chunksize
        r = xrange(c)
        for dx in r:
            for dz in r:            
                h = int(heightfunc(x+dx,z+dz))
                if y <= h:
                    if h < y+c:
                        i = chunk.pos_to_i((dx,h,dz))
                        n = (h-y)
                    else:
                        i = chunk.pos_to_i((dx,c-1,dz))
                        n = c-1
                    chunk[i-n*c:i+1:c] = block_name
    return terrain_generator

def grashoehe(x,z):
    return int(heightfunction(x,z))#int(5*math.sin(x/5.0)+5*math.sin(z/5.0)+5*math.sin(x/5.0+z/5.0))

def erdhoehe(x,z):
    return grashoehe(x,z)-1

def steinhoehe(x,z):
    return grashoehe(x,z)-3

def baum_function(chunk):
    chunksize = 2**chunk.world.chunksize
    chunkpos = chunk.position*chunksize
    baumzahl = random.randint(1,3)
    for i in range(3):
        dx = random.choice(range(chunksize))
        dz = random.choice(range(chunksize))
        baumhoehe = random.randint(3,5)
        x = chunkpos[0] + dx
        z = chunkpos[2] + dz
        y = grashoehe(x,z)
        baumtyp = "eiche"
        for d_pos, block in tree.tree_structure(baumtyp):
            dx, dy, dz = d_pos
            chunk.set_block((x+dx,y+dy,z+dz),block)

spawnpoint = (0,int(heightfunction(0,0)+10),0)
