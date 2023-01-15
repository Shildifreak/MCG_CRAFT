from voxelengine.server.blocks.block_world_view import BlockWorldView

class Block(dict):
	"""convenience class for handling block data"""
	__slots__ = ("position","blockworld")
	
	def __init__(self, data, position=None, blockworld=None):
		assert type(self) != Block #this is an abstract class, please instantiate specific subclasses

		super().__init__(data)
		self.position = position
		self.blockworld = blockworld

	world = property(lambda self: self.blockworld.world)

	relative = property(lambda self: BlockWorldView(self.blockworld, self.position))

	def __eq__(self,other):
		if isinstance(other,dict):
			return dict.__eq__(self,other)
		elif isinstance(other,str):
			return self["id"] == other
		else:
			return False
	def __ne__(self,other):
		return not (self == other)
	
	def __hash__(self):
		return object.__hash__(self)
	
	def client_version(self):
		orientation = self.get("base","")+str(self.get("rotation",""))
		orientation = orientation.strip("b0")
		blockmodel = self["id"]+self.get("state","")
		if orientation:
			return blockmodel+":"+orientation
		else:
			return blockmodel

	def get_tags(self):
		"""to be replaced by subclass if block should react to events"""
		return set()
	
	def handle_events(self, events):
		"""to be replaced by subclass if block should react to events"""
		raise NotImplementedError("Don't know how to handle events")
	
	def save(self):
		"""make changes that were applied to this Block persistent in the world"""
		self.blockworld[self.position] = self

class GenericBlock(Block):
	__slots__ = ()

def BlockFactory(data, *args, **kwargs):
    if isinstance(data, str):
        data = {"id":data}
    return GenericBlock(data, *args, **kwargs)
