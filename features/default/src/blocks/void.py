from resources import *

@register_block("VOID")
class VoidBlock(Block):
	def handle_event_entity_enter(self,events):
		for event in events:
			entity = event.data
			entity.take_damage(1)
		return False

	def get_tags(self):
		return (super().get_tags() - {"solid"}) | {"entity_enter"}
