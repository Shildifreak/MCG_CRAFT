#* encoding: utf-8 *#

import voxelengine

w = voxelengine.World()

with voxelengine.Game( spawnpoint=(w,(0,0,0)) ) as g:
    w.set_block((-1,-2,-3),"GRASS")