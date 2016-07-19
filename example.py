#* encoding: utf-8 *#

import voxelengine

w = voxelengine.World()

with voxelengine.Game(w.spawn_player) as g:
    w.set_block((-1,-2,-3),"BLACK")