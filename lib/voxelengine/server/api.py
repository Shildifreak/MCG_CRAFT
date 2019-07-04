__package__ = "tests"
import sys
sys.path.append("..")
from . import fixpoint

class EntityWorld(object):
	def find_entity(self, area, tag):
		"""entities may be different in size in regards to different tags"""


class BlockWorld(object):
	pass



class BlockStorage(object):
	def __init__(self, blocks, timestamp, retention_period = -1, reference_delete_callback = lambda block_id:None):
		"""retention_period: how many ticks to provide an accurate backlog for (-1 for full history)"""
	def set_timestep(self, timestamp):
		"""current time of the world - used as default timestamp for get_block_id and set_block_id"""
	def get_block_id(self, position, timestep=-1, relative_timestep=True):
		pass
	def set_block_id(self, position, block_id = NO_BLOCK_ID):
		"""
		always manipulates block at current timestamp
		use block_id = NO_BLOCK_ID to delete blocks
		"""
	def __repr__(self):
		pass

class BlockDataEncoder(object):
	def __init__(self, block_codec_and_counter):
		pass
	def get_block_by_id(self, block_id):
		pass
	def get_id_by_block(self, block):
		pass
	def decrease_count(block_id):
		pass
	def increase_count_and_get_id(self, block):
		pass

class BlockWorldIndex(object):
	def __init__(self, get_tags_for_position):
		self._block_tag_cache = dict() #{BinaryBox: {tag:number_of_affected_blocks}}
		self.get_tags_for_position = get_tags_for_position
	
	def notice_change(self, position):
		pass
	
	def find_blocks(self, area, tag, count=None, order=None, point=None):
		"""
		find blocks in a certain area that match a given tag
		return positions of those blocks (+ content?)
		count: how many blocks to find at most
		order: ascending, descending, random, don't care
		point: used to define a distance for ordering
		use for something like "ordered ascending by distance to 0,0,0"
		"""
		pass

class EventSystem(object):
	def add_event(self, event_tag, area, delay, event_data):
		"""
		in <delay> ticks, search for entities and blocks in <area> that registered for <event_tag> and call them back with event_data

		example event_tags:
			renderdistance # use for things like mob movement that should only occur when near players, or update of beacon blocks etc.
			block_update   # I don't know, maybe that's not specific enough, but for stuff like blocks being pushed, placed, broken, etc.
			redstone_update
			hitbox_update  # call for every entity and use for things like collision, pressure plates, ...
			explosion
			random_tick    # get's randomly created around players
			
		"""
		# there should be some way to make sure events like renderdistance only get called once, even when theres multiple players in the area

class World(object):
	def __init__(self, savefile, generator):
		
		data = WORLD_DATA #M#
		metadata = data["metadata"]
		self.entities = EntityWorld()
		self.blocks = BlockWorld(data["blocks"], metadata["timestamp"])
		self.event_system = EventSystem()
		self.metadata = None
		self.seed = None
		pass

	def get_block(self, position):
		# get_block_id
		# translate_from_block_id
		# if no block there use terrain_generator
		if timestep == 0:
			return self.terrain_generator[position]
		pass
	def set_block(self, position, value):
		# translate to block_id
		# check with terrain_generator to see if to delete
		# delete or set
		# update BlockWorldIndex
		pass
	def save(self):
		pass
	def tick(self):
		pass
