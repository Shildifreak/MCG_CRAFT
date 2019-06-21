import blockdata_encoder
import block_storage
import block_world_index




class BlockWorld(object):
	def __init__(self):
		self.event_system = event_system
		
		self.blockdata_encoder = blockdata_encoder.BlockDataEncoder(block_codec_and_counter)
		self.block_storage     = block_storage.BlockStorage(blocks, timestamp, retention_period, reference_delete_callback)
		self.block_world_index = block_world_index.BlockWorldIndex(self.get_tags)
		
		
	def get_tags(self, position):
		pass
	pass
			# make sure to update block tag cache in set_block
