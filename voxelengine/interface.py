#* encoding: utf-8 *#

# voxelengine: a pyglet based voxel engine module for Python
#
# Copyright (C) 2015 - 2016  Joram Brenz
# email: joram.brenz@online.de
#
# This software is provided 'as-is', without any express or implied
# warranty.  In no event will the authors be held liable for any damages
# arising from the use of this software.
#
# Permission is granted to anyone to use this software for any purpose,
# including commercial applications, and to alter it and redistribute it
# freely, subject to the following restrictions:
#
# 1. The origin of this software must not be misrepresented; you must not
#    claim that you wrote the original software. If you use this software
#    in a product, an acknowledgment in the product documentation would be
#    appreciated but is not required.
# 2. Altered source versions must be plainly marked as such, and must not be
#    misrepresented as being the original software.
# 3. This notice may not be removed or altered from any source distribution.


"""
a pyglet based voxel engine module for Python

Dieses Modul soll eine einfache Möglichkeit bieten um 3D/Würfel basierte
Programme zu schreiben.

This module is designed to provide a simple interface for 3D voxel based
applications.

Beispiel/Example:
>>> import voxelengine
>>> w = voxelengine.Blockworld()
>>> with voxelengine.Game( spawnpoint=(w,(0,0,0)) ) as g:
>>>     w.set_block((1,2,3),"GRASS")

"""

__version__ = '0.1.0'

class Game(object):
    """
    Ein Game Objekt sorgt für die Kommunikation mit dem/den Klienten.
    Bei Mehrbenutzerprogrammen muss jeder Benutzer sich mittels des
    Programms voxelengine/client.py verbinden.

    Es ist empfehlenswert Game mit einem with Statement zu benutzen:
    >>> with Game(*args,*kwargs) as g:
    >>>     ...

    args (Argumente):
        spawnpoint : (world, (x,y,z)) where to place new players

    kwargs (Optionale Argumente):
        wait       : wait for players to disconnect before leaving with
        multiplayer: True  - open world to lan
                     False - open client with direct connection
        texturepath: specify path to custom texture.png
        textureinfo: see voxelengine/multiplayer/texture.py
    """
    def __init__(self,spawnpoint,wait=True,multiplayer=False,texturepath=None,textureinfo=None):
        self.spawnpoint = spawnpoint
        self.wait = wait
        self.multiplayer = multiplayer
        self.texturepath = texturepath
        self.textureinfo = textureinfo

    def __enter__(self):
        """for use with "with" statement"""
        pass

    def __exit__(self,*args):
        """for use with "with" statement"
        if wait, wait for someone to end the game"""
        while self.wait and self.get_players():
            self.update()

    def update(self):
        """call regularly to make sure internal updates are performed"""

    def get_players(self):
        """return list of connected players"""

class Blockworld(object):
    def __init__(self):
        """create new Blockworld instance"""

    def get_block(self,(x,y,z)):
        """return ID of block at x,y,z"""

    def set_block(self,(x,y,z),BlockID):
        """set ID of block at x,y,z"""

    def get_entities(self):
        """return list of entities in world"""

class Entity(object):
    def get_pos(self):
        """return position of camera/player"""

    def set_pos(self,(x,y,z)):
        """set position of camera/player"""

    def get_focused_pos(self,max_distance=8):
        """return position of block the player is pointing at
        returns None if there is no block within max_distance"""

    def get_sight_vector(self):
        """returns the current line of sight vector indicating the direction
        the player is looking.
        """

class Player(Entity):
    """a player is an Entity with some additional methods"""
    def is_pressed(self,key):
        """return whether key is pressed """

    def was_pressed(self,key):
        """return whether key was pressed since last update"""
