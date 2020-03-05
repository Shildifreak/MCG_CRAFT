import functools

from voxelengine.modules.world_generation import WorldGenerator
from voxelengine.server.blocks.blockdata_encoder import BlockDataEncoder
from voxelengine.server.blocks.block_storage import BlockStorage
from voxelengine.server.blocks.block_world_index import BlockWorldIndex
from voxelengine.server.blocks.block import Block
from voxelengine.server.event_system import Event
from voxelengine.modules.frozen_dict import freeze
from voxelengine.modules.geometry import Vector, BinaryBox, Sphere
from voxelengine.modules.utils import Serializable

class BlockWorld(Serializable):
	BlockClass = Block #access via self.BlockClass so that it can be overwritten on a per instance basis
	def __init__(self, world, block_world_data, event_system, clock):
		self.event_system = event_system
		
		self.blockdata_encoder = BlockDataEncoder(block_world_data["codec"])
		self.block_storage     = BlockStorage(	blocks = block_world_data["blocks"],
												clock = clock,
												#retention_period,
												reference_delete_callback = self.blockdata_encoder.decrement_count)
		self.block_world_index = BlockWorldIndex(self.get_tags)
		self.world_generator   = WorldGenerator(block_world_data["generator"])
		self.world = world
	
	def __serialize__(self):
		return {"generator" : self.world_generator.generator_data,
		        "blocks"    : self.block_storage,
		        "codec"     : self.blockdata_encoder,
		        }
	
	def _block_by_id(self, block_id, position):
		if block_id == self.block_storage.NO_BLOCK_ID:
			blockdata = self.world_generator.terrain(position)
		else:
			blockdata = self.blockdata_encoder.get_blockdata_by_id(block_id)
		block = self.BlockClass(blockdata, position=position, blockworld=self)
		return block
	
	def __getitem__(self, position, t = 0, relative_timestep = True):
		position = Vector(position)
		block_id = self.block_storage.get_block_id(position, t, relative_timestep)
		return self._block_by_id(block_id, position)
	
	get = __getitem__
	
	def __setitem__(self, position, value):
		position = Vector(position)
		# create a block object, or if already given one, make sure position and world match
		block = self.BlockClass(value, position=position, blockworld=self) #M# maybe don't create new block object if one is given
		# check with terrain_generator to see if to delete
		natural_blockdata = self.world_generator.terrain(position)
		# translate to block_id (delete or set)
		if block == natural_blockdata:
			block_id = self.block_storage.NO_BLOCK_ID
		else:
			blockdata = freeze(block)
			block_id = self.blockdata_encoder.increment_count_and_get_id(blockdata)
		# apply
		block_changed = self.block_storage.set_block_id(position, block_id)
		if block_changed:
			# update BlockWorldIndex
			self.block_world_index.notice_change(position, block.get_tags())
			# issue event for others to notice change
			#self.event_system.add_event(0,Event("block_update",BinaryBox(0,position).bounding_box(),block)) #since it's 0 delay there is no problem with passing unfrozen object
			self.event_system.add_event(0,Event("block_update",Sphere(position,1.2),block)) #since it's 0 delay there is no problem with passing unfrozen object
		
	def get_tags(self, position):
		return self[position].get_tags()

	@functools.wraps(BlockWorldIndex.find_blocks)
	def find_blocks(self, *args, **kwargs):
		for position in self.block_world_index.find_blocks(*args, **kwargs):
			yield self[position]

	@functools.wraps(BlockStorage.list_changes)
	def list_changes(self, area, since_tick):
		for position, block_id in self.block_storage.list_changes(area, since_tick):
			yield position, self._block_by_id(block_id, position)
