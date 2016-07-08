class Game(object):
    def get_players(self):
        """return list of connected players"""

class Blockworld(object):
    def __init__(self, open_to_lan=False, open_client=True):
        """create new Blockworld instance"""
        
    def update(self):
        """call regularly to make sure internal updates are performed"""

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

