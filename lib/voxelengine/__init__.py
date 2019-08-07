#* encoding: utf-8 *#

u"""
a pyglet based voxel engine module for Python

Dieses Modul soll eine einfache Möglichkeit bieten um 3D/Würfel basierte
Programme zu schreiben.

This module is designed to provide a simple interface for 3D voxel based
applications.
"""
#M# The following example is not up to date!
"""
Beispiel/Example:
>>> import voxelengine
>>> w = voxelengine.World()
>>> with voxelengine.Game( spawnpoint=(w,(0,0,0)) ) as g:
>>>     w.set_block((1,2,3),"GRASS")

"""

__version__ = '0.1.0'
__all__ = []

#from server import *
#import voxelengine.client as client

__all__.extend(filter(lambda s:not s.startswith("_"),globals().keys()))
