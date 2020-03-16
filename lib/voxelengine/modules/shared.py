# The shared.py file contains information that is relevant to client and server but does not depend on the game

import sys, os, inspect
if __name__ == "__main__":
    sys.path.append(os.path.abspath("../.."))
    __package__ = "voxelengine.modules"
# PATH = DONT DEFINE PATH SINCE SHARED IS OFTEN IMPORTED FROM WITH *
from collections import namedtuple
from voxelengine.modules.geometry import Vector



# list of possible events, order of bytes to transmit
ACTIONS = ["inv1","inv2","inv3","inv4","inv5","inv6","inv7","inv8","inv9","inv0",
#               2      4      8     16     32     64    128    256    512   1024
           "for" ,"back","left","right","jump","fly","inv","shift","sprint","left_hand","right_hand"]
#           2048    4096   8192   16384  32768  65536  ...    ...      ...

# the dimension of the game (used to avoid magic numbers in code)
DIMENSION = 3 # but please don't change it, it won't work, there are a lot of places where variables for x,y,z are hardcoded

# enums for placing UI elements, base 2 so they can be combined with bit logic
CENTER, INNER, OUTER, TOP, BOTTOM, LEFT, RIGHT = 0,1,2,4,8,16,32

# the directions of the world
Faces = namedtuple("Faces",["TOP","BOTTOM","FRONT","BACK","LEFT","RIGHT"])
FACES = Faces(Vector([ 0, 1, 0]), #FACES.TOP
              Vector([ 0,-1, 0]), #FACES.BOTTOM
              Vector([ 0, 0, 1]), #FACES.FRONT
              Vector([ 0, 0,-1]), #FACES.BACK
              Vector([-1, 0, 0]), #FACES.LEFT
              Vector([ 1, 0, 0])) #FACES.RIGHT
