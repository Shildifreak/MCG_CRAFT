import bisect

import sys
sys.path.append("..")

class BlockDataEncoder(object):
	"""doesn't care about mutability of blockdata, copy et simile has to be done somewhere else"""
	def __init__(self, block_codec_and_counter):
		self.block_codec, self.counter = map(list, zip(*block_codec_and_counter) if block_codec_and_counter else ((),())) #[data_0, data_1, ..., data_n] [count_0, count_1, ..., count_n]   (zip doesn't work if its empty, because it can't know number of sequences to generate)

		print(self.block_codec, self.counter)

		self.index = {h:i for i,h in enumerate(self.block_codec)}
		self.unused_indices = [i for i,c in enumerate(self.counter) if c <= 0] #sorted list of indices

	def get_blockdata_by_id(self, block_id):
		return self.block_codec[block_id]

	def get_id_by_blockdata(self, blockdata):
		return self.index[blockdata]

	def decrement_count(self, block_id):
		self.counter[block_id] -= 1
		if self.counter[block_id] <= 0:
			bisect.insort(self.unused_indices, block_id)

	def increment_count_and_get_id(self, blockdata):
		try:
			i = self.index[blockdata]
		except KeyError:
			i = self._claim_id(blockdata)
		self.counter[i] += 1
		return i

	def _claim_id(self, blockdata):
		"""replace unused entry or create a new one and return the id"""
		if self.unused_indices:
			i = self.unused_indices.pop(0)
			i_popped = self.index.pop(self.block_codec[i]) # if this ...
			assert i_popped == i # ... or this fails then the hashable representation of a value changed, which in itself should not happen, because the values are assumed to be immutable or at least not actually mutating
			self.block_codec[i] = blockdata
			self.counter[i] = 0
		else:
			i = len(self.block_codec)
			self.block_codec.append(blockdata)
			self.counter.append(0)
		self.index[blockdata] = i
		return i

	def __repr__(self):
		return repr(tuple(zip(self.block_codec, self.counter)))

	def check_and_cleanup(self):
		"""
		delete data of unused ids (the ones at the end of the list can be completely removed)
		check if index matches _to_hashable results to see if one of the assumed to be not changing blockdata changed 
		"""

if __name__ == "__main__":
	from modules.frozen_dict import *
	
	bde = BlockDataEncoder([("a",1),("b",2)])

	print(bde.increment_count_and_get_id(freeze({"id":"STONE","state":2})))
	i = bde.increment_count_and_get_id(freeze({"id":"STONE","state":2}))
	print(bde.increment_count_and_get_id(freeze({"state":2,"id":"STONE"})))
	print(bde)
	bde.decrement_count(i)
	bde.decrement_count(i)
	print(bde)
	print(bde.increment_count_and_get_id(freeze({"id":"AIR"})))
	print(bde.increment_count_and_get_id(freeze({"id":"MUD"})))
	print(bde)
