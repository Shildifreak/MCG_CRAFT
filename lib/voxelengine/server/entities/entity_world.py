
from voxelengine.server.entities.entity import Entity
from voxelengine.modules.geometry import EVERYWHERE
from voxelengine.modules.serializableCollections import Serializable

class EntityWorld(Serializable):

	def __init__(self, data):
		self.next_id = data["next_id"]
		self.entities = set()
		for entity in data["entities"]:
			self.entities.add(Entity(entity))
	
	def __serialize__(self):
		return {"next_id" : self.next_id,
		        "entities": list(self.entities)
		        }

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
