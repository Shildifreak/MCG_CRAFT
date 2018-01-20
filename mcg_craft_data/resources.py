items = {}
blocks = {}

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

class Item(object):
	model = """<Entity Model>"""
	icon = """<sometexture_name>"""

	def __init__(self,item_data):
		self.data = item_data

	def right_click_on_block(self,player,blockpos,face,world):
		"""something like placing block depending on direction player is looking"""

	def left_click_on_block(self,player,blockpos,face,world):
		"""most likely mining the block"""

	def right_click_on_entity(self,player,entity):
		"""whatever this item should do when clicked on this entity"""

	def left_click_on_entity(self,player,entity):
		"""punching with sword etc."""

class Block(object):
	textures = "STEIN"

	def __init__(self):
		raise NotImplementedError("This class is for Interface use only, you shouldn't instanciate it.")

	def block_updated(self,directions):
		"""directions indicates where updates came from... usefull for observer etc."""
		"""manipulate world with setblock to update the block if neccessary (which gets buffered for synchronity and automatically evokes block update)"""

	def random_ticked():
		"""spread grass etc"""

	def right_clicked(player,blockpos,world):
		"""something like placing block depending on direction player is looking"""

	def mined(player):
		"""drop item or something... dont set block to air, that is done automagically"""

#####################################################################################

@register_item("mcgcraft:stone")
class StoneItem(Item):
	icon = (0,0)

	def right_click_on_block(self,character,blockpos,face,world):
		world.set_block(blockpos+face,"minecraft:stone")
		inv = player["inventory"]
		charakter.set_slot(self.data["slot"],"air")

	def left_click_on_block(self,player,blockpos,face,world):
		"""most likely mining the block"""

	def right_click_on_entity(self,player,entity):
		"""whatever this item should do when clicked on this entity"""

	def left_click_on_entity(self,player,entity):
		"""punching with sword etc."""

@register_block("mcgcraft:stone")
class StoneBlock(Block):
	textures = "STEIN"

	def block_updated(self,directions):
		"""directions indicates where updates came from... usefull for observer etc."""
		"""manipulate world with setblock to update the block if neccessary (which gets buffered for synchronity and automatically evokes block update)"""

	def random_ticked():
		"""spread grass etc"""

	def right_clicked(player,blockpos,world):
		"""something like placing block depending on direction player is looking"""

	def mined(player):
		"""drop item or something... dont set block to air, that is done automagically"""
	
