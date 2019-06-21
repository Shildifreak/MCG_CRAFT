import bisect

class BlockStorage(object):
	NO_BLOCK_ID = -1 #use to delete blocks
	def __init__(self, blocks, clock, retention_period = -1, reference_delete_callback = lambda block_id:None):
		"""
		retention_period: how many ticks to provide an accurate backlog for (-1 for full history)
		clock: has to have attribute current_timestep that may only ever increase
		"""
		self.clock = clock
		self.structures = dict(blocks) #{(x,y,z):[(t1,block_id),(t2,block_id)]} | where t1 <= t2
		self.retention_period = retention_period

	def _cleanup_history(self, block_history):
		"""check if there are entries that are expired and remove them"""
		if self.retention_period < 0:
			pass
		else:
			raise NotImplementedError()
			# don't forget reference_delete_callback to inform Block Encoder
			# also don't forget special handling for NOT_A_BLOCK_ID
	
	def get_block_id(self, position, timestep=-1, relative_timestep=True):
		""" if block is not found returns self.NO_BLOCK_ID"""
		try:
			block_history = self.structures[position]
		except KeyError:
			return self.NO_BLOCK_ID
		if relative_timestep:
			timestep += self.clock.current_timestep
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
		"""
		# warn if manipulating same block multiple times?
		try:
			block_history = self.structures[position]
		except KeyError:
			block_history = []
			self.structures[position] = block_history
		# append, not replace even if same timestep. otherwise reference_delete_callback would have to be called
		block_history.append((self.clock.current_timestep, block_id))
		self._cleanup_history(block_history)

	def __repr__(self):
		return repr(self.structures)
	

if __name__ == "__main__":
	# TEST CASES
	class Clock(object):
		current_timestep = 0
	clock = Clock()

	bs = BlockStorage(blocks = {}, clock = clock)

	bs.set_block_id((0,0,0), 5)
	clock.current_timestep = 1
	print(bs.get_block_id((0,0,0)))

	bs.set_block_id((0,0,0), 4)
	clock.current_timestep = 2
	print(bs.get_block_id((0,0,0)))

	if (bs.get_block_id((0,0,0), -10)) is BlockStorage.NO_BLOCK_ID:
		print("unknown history worked")
	else:
		print("unknown history failed")

	bs.set_block_id((0,0,0))
	clock.current_timestep = 3
	if (bs.get_block_id((0,0,0))) is BlockStorage.NO_BLOCK_ID:
		print("deleting worked")
	else:
		print("deleting failed")
	
	print(repr(bs))
