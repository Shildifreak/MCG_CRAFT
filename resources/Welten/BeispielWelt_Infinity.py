
import tree
from voxelengine.modules.geometry import Vector

def init(world):
    base = Vector(0,0,-8)
    for position, block in tree.tree_structure("eiche"):
        world.blocks[base + position] = block
