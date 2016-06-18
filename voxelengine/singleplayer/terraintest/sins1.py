import math
random_waves = True
if random_waves:
    k = 7
    n = 4
    m = 2
    import random
    waves = []
    for i in range(1,n):
        for _ in range(m):
            f = random.expovariate(k**i)
            ff = random.expovariate(k**(i+1))
            w = random.random()*2*math.pi
            w2 = random.random()*2*math.pi
            fx = math.cos(w)*f
            fz = math.sin(w)*f
            ffx = math.cos(w2)*ff
            ffz = math.sin(w2)*ff
            a = (0.4*(0.5+random.random())/f)**0.7
            if random.randint(0,1):
                a *= -1
            waves.append((a,fx,fz,ffx,ffz))
else:
    waves = [#amplitude, frequenzy_x, frequenzy_y, frequenzy_faktor_x, frequenzy_faktor_y
            ( 3,  0.1,  0,0,0),
            (10,0.011,  0,0,0),
            ( 3,    0,0.1,0,0),]
distort_waves = [(1,1),(10,0.09),(-7,0.3)]
distort_waves2 = [(9,0.07),(-4,0.4)]

def g(x,z):
    for a,f in distort_waves:
        x, z = x+a*math.sin(f*z), z+a*math.sin(f*x)
    for a,f in distort_waves2:
        x += a*math.sin(f*x)
        z += a*math.sin(f*z)

    y = sum([a*math.sin(fx*x+fz*z)*math.cos(ffx*x+ffz*z) for a,fx,fz,ffx,ffz in waves])
    return y

from display2d import display
display(g)