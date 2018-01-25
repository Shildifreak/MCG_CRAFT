import collections

items  = collections.defaultdict(lambda:Item)
blocks = collections.defaultdict(lambda:Block)

def register_item(name):
    def _register_item(item_subclass):
        items[name] = item_subclass
        return item_subclass
    return _register_item

def register_block(name):
    def _register_block(block_subclass):
        blocks[name] = block_subclass
        return block_subclass
    return _register_block

# Default Item and Block (also usefull for inheritance)

class Item(object):
    def __init__(self,item):
        self.item = item
        self.tags = item.setdefault("tags",{})

    # FUNCTIONS TO BE OVERWRITTEN IN SUBCLASSES:
    def use_on_block(self,character,blockpos,face):
        """something like placing block depending on direction character is looking"""
        new_pos = blockpos + face
        kind = self.item["id"]
        character.world[new_pos] = kind
        #M# remove grass if it collides with placer (check for all entities here later)
        if new_pos in character.collide(character["position"]):
            character.world[new_pos] = "AIR"        

    def use_on_entity(self,character,entity):
        """whatever this item should do when clicked on this entity"""
        self.use_on_air(character)

    def use_on_air(self,character):
        """whatever this item should do when clicked into air"""

class Block(object):
    def __init__(self, world, position):
        self.world = world
        self.position = position

    def block_update(self,directions):
        """directions indicates where updates came from... usefull for observer etc."""
        """for pure cellular automata action make sure to only change the block itself"""

    def random_ticked(self):
        """spread grass etc"""

    def activated(self,character):
        """blocks like levers should implement this action. Return value signalizes whether to execute use action of hold item"""
        return True

    def mined(self,character):
        """drop item or something... also remember to set it to air. Return value see activated"""
        block_id = self.world[self.position]
        character["right_hand"] = {"id":block_id}
        self.world[self.position] = "AIR"
