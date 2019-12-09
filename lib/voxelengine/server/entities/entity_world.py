from voxelengine.modules.geometry import EVERYWHERE

class EntityWorld(object):

	def __init__(self):
		self.entities = set()

	def find_entities(self, area=EVERYWHERE, tags=frozenset()):
		"""entities may be different in size in regards to different tags"""
		#entities are added into binary box tree by their binary box cover[s] for the corresponding tags
		#when searching build a set of all possibly affected entities
		#then do a real test on the hitboxes
		if isinstance(tags, str):
			tags = {tags} #M# could use frozenset instead
		for entity in self.entities:
			if tags.issubset(entity["tags"]):
				if area.collides_with(entity.HITBOX + entity["position"]):
					yield entity

	def notice_move(self, entity, old_position, new_position):
		pass

	def add(self, entity):
		self.entities.add(entity)

	def remove(self, entity):
		self.entities.remove(entity)
