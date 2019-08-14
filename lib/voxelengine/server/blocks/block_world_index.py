import sys
if __name__ == "__main__":
	sys.path.append("../../..")
	__package__ = "voxelengine.server.blocks"

import collections
from voxelengine.modules.geometry import BinaryBox

class BlockWorldIndex(object):
	def __init__(self, get_tags_for_position):
		self._block_tag_cache = dict() #{BinaryBox: {tag:number_of_affected_blocks}}
		self.get_tags_for_position = get_tags_for_position
	
	def notice_change(self, position, new_tags=None):
		"""new_tags can be provided to avoid overhead of calling get_tags_for_position, but it has to be the same tags"""
		if new_tags == None:
			new_tags = get_tags_for_position(position)
		#assert new_tags == get_tags_for_position(position)
		bb = BinaryBox(position, 0)
		if bb not in self._block_tag_cache:
			return
		# get tags that this block previously had by looking up 1x1x1 BinaryBox, calculate difference for each tag (+1,0,-1) <=> added, kept, removed
		previous_tags = self._block_tag_cache[bb]
		tag_difference = Counter(new_tags)
		tag_difference.subtract(previous_tags)
		# apply that change to BinaryBox and all parents
		while bb in self._block_tag_cache:
			tag_counter = self._block_tag_cache[bb]
			tag_counter.update(tag_difference)
			bb.get_parent()
	
	def _get_tag_counter(self, binary_box):
		# look for existing entry
		if binary_box in self._block_tag_cache:
			return self._block_tag_cache[binary_box]
		# create new entry
		if binary_box.scale == 0:
			counter = collections.Counter(self.get_tags_for_position(binary_box.position))
		else:
			counter = collections.Counter()
			for child in binary_box.get_children():
				counter.update(self._get_tag_counter(child))
		self._block_tag_cache[binary_box] = counter
		return counter

	def _get_tags(self, binary_box):
		return set(k for k,v in self._get_tag_counter(binary_box) if v > 0)
	
	def find_blocks(self, area, tags, count=None, order=None, point=None):
		"""
		find blocks in a certain area that match all given tags
		return positions of those blocks (+ content?)
		area: Area object
		tags: string or set of strings
		count: how many blocks to find at most
		order: ascending, descending, random, don't care
		point: used to define a distance for ordering
		use for something like "ordered ascending by distance to 0,0,0"
		"""
		if count != None:
			raise NotImplementedError()
		if order != None:
			raise NotImplementedError()
		if point != None:
			raise NotImplementedError()
		if isinstance(tags, str):
			tags = {tags}
		assert isinstance(tags, set)

		# get binary box cover of area
		# get tags for those boxes, if necessary generate the tags
		# if box is more than one block in size, repeat recursively with subboxes
		bbs = list(area.binary_box_cover()) #M# could try to find a way to stream this generator and join it with queue of children, (or just do depth first)
		while bbs:
			bb = bbs.pop(0)
			bb_tags = self._get_tags(bb)
			if tags.issubset(bb_tags) and bb.collides_with(area): #M# could try to swap and see how performance changes
				if bb.scale == 0:
					yield bb.position
				else:
					bbs.extend(bb.get_children())
