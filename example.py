#* encoding: utf-8 *#

import voxelengine

help(voxelengine)

w = voxelengine.Blockworld()

with voxelengine.Game( spawnpoint=(w,(0,0,0)) ) as g:
    """hier könnte dein Programm stehen"""