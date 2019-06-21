import bisect

class BlockStorage(object):
	NO_BLOCK_ID = float("nan") #use to delete blocks
	def __init__(self, blocks, timestamp, retention_period = -1, reference_delete_callback = lambda block_id:None):
		"""retention_period: how many ticks to provide an accurate backlog for (-1 for full history)"""
		self.current_timestep = timestamp
		self.structures = dict(blocks) #{(x,y,z):[(t1,block_id),(t2,block_id)]} | where t1 <= t2
		self.retention_period = retention_period
	
	def set_timestep(self, timestep):
		"""current time of the world - used as default timestamp for get_block_id and set_block_id"""
		self.current_timestep = timestep
	
	def _cleanup_history(self, block_history):
		"""check if there are entries that are expired and remove them"""
		if self.retention_period < 0:
			pass
		else:
			raise NotImplementedError()
			# don't forget reference_delete_callback to inform Block Encoder
			# also don't forget special handling for NOT_A_BLOCK_ID
	
	def get_block_id(self, position, timestep=-1, relative_timestep=True):
		""" """
		if relative_timestep:
			timestep += self.current_timestep
		block_history = self.structures[position]
		threshold = (timestep,float("inf"))
		i = bisect.bisect_right(block_history, threshold) - 1
		if i < 0:
			raise KeyError() #timestep is before first history entry
		block_id = block_history[i][1]
		if block_id is BlockStorage.NO_BLOCK_ID: #can't use == cause that doesn't work with NAN
			raise KeyError() #block was deleted, so there's no block for this key
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
		block_history.append((self.current_timestep, block_id))

	def __repr__(self):
		return repr(self.structures)
	

if __name__ == "__main__":
	# TEST CASES

	bs = BlockStorage(blocks = {}, timestamp = 0)

	bs.set_block_id((0,0,0), 5)
	bs.set_timestep(1)
	print(bs.get_block_id((0,0,0)))

	bs.set_block_id((0,0,0), 4)
	bs.set_timestep(2)
	print(bs.get_block_id((0,0,0)))

	try:
		print(bs.get_block_id((0,0,0), -10))
	except KeyError:
		print("unknown history worked")
	else:
		print("unknown history failed")

	bs.set_block_id((0,0,0))
	bs.set_timestep(3)
	try:
		print(bs.get_block_id((0,0,0)))
	except KeyError:
		print("deleting worked")
	else:
		print("deleting failed")
	
	print(repr(bs))
