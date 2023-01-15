import functools

from voxelengine.modules.world_generation import WorldGenerator
from voxelengine.server.blocks.blockdata_encoder import BlockDataEncoder
from voxelengine.server.blocks.block_storage import BlockStorage
from voxelengine.server.blocks.block_world_index import BlockWorldIndex
from voxelengine.server.blocks.block import Block #this is only the base class, use BlockFactory for specific blocks
from voxelengine.server.event_system import Event
from voxelengine.modules.frozen_dict import freeze
from voxelengine.modules.geometry import Vector, BinaryBox, Sphere
from voxelengine.modules.serializableCollections import Serializable

class BlockWorld(Serializable):
	def __init__(self, world, block_world_data, event_system, clock, blockFactory):
		self.event_system = event_system
		self.BlockFactory = blockFactory
		
		block_codec_and_counter = [(freeze(block), count) for block, count in block_world_data["codec"]]
		blocks = [(Vector(position), block_history) for position, block_history in block_world_data["blocks"]]

		self.blockdata_encoder = BlockDataEncoder(block_codec_and_counter)
		self.block_storage     = BlockStorage(	blocks = blocks,
												clock = clock,
												#retention_period,
												reference_delete_callback = self.blockdata_encoder.decrement_count)
		self.block_world_index = BlockWorldIndex(self.get_tags)
		self.world_generator   = WorldGenerator(block_world_data["generator"])
		self.world = world
		self.write_lock = ContextCounter()
	
	def __serialize__(self):
		return {"generator" : self.world_generator.generator_data,
		        "blocks"    : self.block_storage,
		        "codec"     : self.blockdata_encoder,
		        }
	
	def _blockdata_by_id(self, block_id, position):
		if block_id == self.block_storage.NO_BLOCK_ID:
			return self.world_generator.terrain(position)
		else:
			return self.blockdata_encoder.get_blockdata_by_id(block_id)
	
	def _get_blockdata(self, position, t = 0, relative_timestep = True):
		position = Vector(position)
		block_id = self.block_storage.get_block_id(position, t, relative_timestep)
		blockdata = self._blockdata_by_id(block_id, position)
		return blockdata
	
	def __getitem__(self, position, t = 0, relative_timestep = True):
		position = Vector(position)
		blockdata = self._get_blockdata(position, t, relative_timestep)
		block = self.BlockFactory(blockdata, position=position, blockworld=self)
		return block
	
	get = __getitem__
	
	def __setitem__(self, position, value):
		if self.write_lock:
			raise RuntimeError("Tried to set block in read only context.")
		position = Vector(position)
		# create a block object, or if already given one, make sure position and world match
		block = self.BlockFactory(value, position=position, blockworld=self) #M# maybe don't create new block object if one is given
		blockdata = freeze(block)
		# check with terrain_generator to see if to delete
		natural_blockdata = self.world_generator.terrain(position)
		# translate to block_id (delete or set)
		if block == natural_blockdata:
			block_id = self.block_storage.NO_BLOCK_ID
		else:
			block_id = self.blockdata_encoder.increment_count_and_get_id(blockdata)
		# apply
		block_changed = self.block_storage.set_block_id(position, block_id)
		if block_changed:
			# update BlockWorldIndex
			self.block_world_index.notice_change(position, self._get_tags(blockdata))
			# issue event for others to notice change
			#self.event_system.add_event(Event("block_update",BinaryBox(0,position).bounding_box(),block)) #since it's 0 delay there is no problem with passing unfrozen object
			self.event_system.add_event(Event("block_update",Sphere(position,1.2),block)) #since it's 0 delay there is no problem with passing unfrozen object
		
	@functools.lru_cache()
	def _get_tags(self, blockdata):
		return self.BlockFactory(blockdata).get_tags()

	@functools.lru_cache()
	def _client_version(self, blockdata):
		return self.BlockFactory(blockdata).client_version()

	def get_tags(self, position):
		return self._get_tags(self._get_blockdata(position))

	@functools.wraps(BlockWorldIndex.find_blocks)
	def find_blocks(self, *args, **kwargs):
		for position in self.block_world_index.find_blocks(*args, **kwargs):
			yield self[position]

	@functools.wraps(BlockStorage.list_changes)
	def list_changes(self, area, since_tick):
		for position, block_id in self.block_storage.list_changes(area, since_tick):
			blockdata = self._blockdata_by_id(block_id, position)
			block_client_version = self._client_version(blockdata)
			yield position, block_client_version

class ContextCounter(object):
	__slots__ = ("count",)
	def __init__(self):
		self.count = 0
	def __enter__(self):
		self.count += 1
	def __exit__(self, *_):
		assert self.count
		self.count -= 1
	def __bool__(self):
		return bool(self.count)
