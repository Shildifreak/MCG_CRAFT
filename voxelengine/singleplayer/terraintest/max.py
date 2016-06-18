import math

def f(x,z):
    x = x/10.
    z = z/10.
    return 10*math.sin(math.sin(x*(2+math.sin(z)/5)/4)*x-math.pi/2)
    return 0

import display3d
display3d.display(f,20)