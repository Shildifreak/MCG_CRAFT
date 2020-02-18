# -*- coding: utf-8 -*-
import random

spawnpoint = (0,5,0)

def terrain(position):
    if position[1] != 0:
        return "AIR"
    else:   
        local_seed = seed + position[0] + position[1] + position[2]
        random.seed(local_seed)
        return random.choice(["STONE","GRASS","DIRT"])

terrain_js = """
function terrain(position) {
    alert("this world has no working javascript world generator");
    return "AIR";
}
"""
