import blockdata_encoder
import block_storage
import block_world_index
import world_generation

class BlockWorld(object):
	BlockClass = Block
	def __init__(self, block_world_data, event_system, clock):
		self.event_system = event_system
		
		self.blockdata_encoder = blockdata_encoder.BlockDataEncoder(block_world_data["codec"])
		self.block_storage     = block_storage.BlockStorage(blocks = block_world_data["blocks"],
															clock = clock,
															#retention_period,
															reference_delete_callback = self.blockdata_encoder.decrement_count)
		self.block_world_index = block_world_index.BlockWorldIndex(self.get_tags)
		self.world_generator   = world_generation.load_generator(block_world_data["generator"])
	
	def __getitem__(self, position, timestep = -1, relative_timestep = True):
		block_id = self.block_storage.get_block_id(position, timestep, relative_timestep)
		if block_id == self.block_storage.NO_BLOCK_ID:
			blockdata = self.world_generator[position]
		else:
			blockdata = self.blockdata_encoder.get_blockdata_by_id(block_id)
		block = BlockClass(blockdata)
		return block
	
	def __setitem__(self, position, value):
		blockdata = freeze(value)
		# check with terrain_generator to see if to delete
		natural_blockdata = self.world_generator[position]
		# translate to block_id (delete or set)
		if blockdata == natural_blockdata:
			block_id = self.block_storage.NO_BLOCK_ID
		else:
			block_id = self.blockdata_encoder.get_id_by_blockdata(blockdata)
		# apply
		block_storage.set_block_id(position, block_id)
		# update BlockWorldIndex
		self.block_world_index.notice_change(position)
		
	def get_tags(self, position):
		return self[position].get_tags()



class Block(object):
	def __new__(cls,data):
		if isinstance(data,basestring):
			data = {"id":data}
		else:
			assert "id" in data
		data = BlockData(data)
	def __init__(self, position, world):
		self.position = position
		self.world = world
	"""
	def __getitem__(self,key):
		return self.data[key]
	def __setitem__(self,key,value=delvalue):
		if self.data.immutable() and (self.chunk != None): # <=> data may be used by multiple Blocks
			self.data = BlockData(self.data.copy())
			self.data[key] = value
			self.chunk.set_block(self.position, self)
		else:
			self.data[key] = value
	def __delitem__(self,key): # make that stuff prettier
		if self.data.immutable() and (self.chunk != None):
			self.data = BlockData(self.data.copy())
			del self.data[key]
			self.chunk.set_block(self.position, self)
		else:
			del self.data[key]
	"""
	def __eq__(self,other):
		if isinstance(other,dict):
			return dict.__eq(self,other)
		elif isinstance(other,basestring):
			return self["id"] == other
		else:
			return False
	def __ne__(self,other):
		return not (self == other)
	
	def client_version(self):
		orientation = self.get("base","")+str(self.get("rotation",""))
		blockmodel = self["id"]+self.get("state","")
		if orientation:
			return blockmodel+":"+orientation
		else:
			return blockmodel

	def tags(self):
		return set()
	
	def save(self):
		"""make changes that were applied to this Block persistent in the world"""
		self.world[self.position] = self
