import collections
import random

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
    # Init function, don't care to much about this
    def __init__(self,item):
        self.item = item
        self.tags = item.setdefault("tags",{})

    # FUNCTIONS TO BE OVERWRITTEN IN SUBCLASSES:
    def use_on_block(self,character,blockpos,face):
        """whatever this item should do when click on a block... default is to place a block with same id"""
        new_pos = blockpos + face
        block_id = self.item["id"]
        character.world[new_pos] = block_id
        #M# remove block again if it collides with placer (check for all entities here later)
        if new_pos in character.collide(character["position"]):
            character.world[new_pos] = "AIR"        

    def use_on_entity(self,character,entity):
        """whatever this item should do when clicked on this entity... default is to do the same like when clicking air"""
        self.use_on_air(character)

    def use_on_air(self,character):
        """whatever this item should do when clicked into air"""

class Block(object):
    blast_resistance = 0
    # Init function, don't care to much about this
    def __init__(self):
        raise NotImplementedError("This Class is only used as 'quasi' superclass, don't instanciate it.")

    # FUNCTIONS TO BE OVERWRITTEN IN SUBCLASSES:
    def block_update(self,directions):
        """directions indicates where update(s) came from... usefull for observer etc."""
        """for pure cellular automata action make sure to not set any blocks but only return new state for this block (use schedule to do stuff that effects other blocks)"""

    def random_ticked(self):
        """spread grass etc"""

    def activated(self,character,face):
        """blocks like levers should implement this action. Return value signalizes whether to execute use action of hold item"""
        return True

    def mined(self,character,face):
        """drop item or something... also remember to set it to air. Return value see activated"""
        block = self.world[self.position]
        character["right_hand"] = {"id":block["id"]}
        self.world[self.position] = "AIR"

    def exploded(self,entf):
        if entf < 1:
            if random.random() > self.blast_resistance:
                self.world[self.position] = "AIR"

    def collides_with(self,entity):
        return True

#######################################################################
#   essential blocks

@register_block("AIR")
class AirBlock(Block):
    def collides_with(self,entity):
        return False

