import sys, os
if __name__ == "__main__":
    sys.path.append(os.path.abspath("../../.."))
    __package__ = "voxelengine.server.blocks"

import bisect
from voxelengine.modules.binary_dict import BinaryDict
from voxelengine.modules.utils import Serializable

class BlockStorage(Serializable):
	NO_BLOCK_ID = -1 #use to delete blocks
	def __init__(self, blocks, clock, retention_period = -1, reference_delete_callback = lambda block_id:None):
		"""
		retention_period: how many ticks to provide an accurate backlog for (-1 for full history)
		clock: has to have attribute current_timestep that may only ever increase
		"""
		self.clock = clock
		self.structures = BinaryDict(blocks)
		#self.structures = dict(blocks) #{(x,y,z):[(t1,block_id),(t2,block_id)]} | where t1 <= t2
		self.retention_period = retention_period

	def __serialize__(self):
		return list(self.structures.items())

	def _cleanup_history(self, block_history):
		"""check if there are entries that are expired and remove them"""
		if self.retention_period < 0:
			pass
		else:
			raise NotImplementedError()
			# don't forget reference_delete_callback to inform Block Encoder
			# also don't forget special handling for NOT_A_BLOCK_ID
	
	def valid_history(self, timestep):
		"""tell if timestamp is older than retention period but not 0 and thereby invalid"""
		if timestep == 0:
			return True
		if self.retention_period < 0:
			return True
		if 0 <= self.clock.current_gametick - timestep <= self.retention_period:
			return True
		return False
	
	def get_block_id(self, position, timestep=0, relative_timestep=True):
		""" if block is not found returns self.NO_BLOCK_ID"""
		try:
			block_history = self.structures[position]
		except KeyError:
			return self.NO_BLOCK_ID
		if relative_timestep:
			timestep += self.clock.current_gametick
		assert self.valid_history(timestep)
		threshold = (timestep,float("inf"))
		i = bisect.bisect_right(block_history, threshold) - 1
		if i < 0:
			return self.NO_BLOCK_ID #timestep is before first history entry
		block_id = block_history[i][1]
		return block_id
	
	def set_block_id(self, position, block_id = NO_BLOCK_ID):
		"""
		always manipulates block at current timestamp
		use block_id = NO_BLOCK_ID to delete blocks
		returns whether the block was changed
		"""
		# warn if manipulating same block multiple times?
		try:
			block_history = self.structures[position]
		except KeyError:
			if block_id == self.NO_BLOCK_ID:
				return False
			block_history = self.structures[position] = []
		else:
			previous_block_id = block_history[-1][1]
			if block_id == previous_block_id:
				return False
		# append, not replace even if same timestep. otherwise reference_delete_callback would have to be called
		block_history.append((self.clock.current_gametick, block_id))
		self._cleanup_history(block_history)
		return True

	def list_changes(self, area, since_tick):
		assert self.valid_history(since_tick)
		for binary_box in area.binary_box_cover():
			for position, history in self.structures.list_blocks_in_binary_box(binary_box):
				if position in area:
					if history:
						t, block_id = history[-1]
						if t >= since_tick:
							yield position, block_id
	

if __name__ == "__main__":
	# TEST CASES
	class Clock(object):
		current_gametick = 0
	clock = Clock()

	bs = BlockStorage(blocks = (), clock = clock)

	bs.set_block_id((0,0,0), 5)
	print(bs.get_block_id((0,0,0)))
	clock.current_gametick = 1

	bs.set_block_id((0,0,0), 4)
	print(bs.get_block_id((0,0,0)))
	clock.current_gametick = 2

	if (bs.get_block_id((0,0,0), -10)) is BlockStorage.NO_BLOCK_ID:
		print("unknown history worked")
	else:
		print("unknown history failed")

	bs.set_block_id((0,0,0))
	clock.current_gametick = 3
	if (bs.get_block_id((0,0,0))) is BlockStorage.NO_BLOCK_ID:
		print("deleting worked")
	else:
		print("deleting failed")
	
	print(repr(bs))
