from resources import *

@register_block("PORTAL")
class Portal(Block):
	
	def handle_event_entity_enter(self,events):
		for event in events:
			entity = event.data
			if entity.world.clock.time - entity.get("t_portal",0) < 10:
				continue
			print("Portal: entity:",entity)
			x,y,z = self.position
			# teleport up or down
			if ((y-5000)//10000) % 2:
				offset = (0, -10000, 0)
			else:
				offset = (0, 10000, 0)
			# find inhabitable position nearby

			# create a portal block at target location
			if self.relative[offset] != "PORTAL":
				self.world.request_set_block(self.position+offset, "PORTAL", priority=99)

			# teleport entity and reset portal timer
			entity["position"] += offset
			entity["t_portal"] = entity.world.clock.time
			
		return False #did not change this portal block

	def get_tags(self):
		return super().get_tags() | {"entity_enter"}

	def collides_with(self,area):
		return False
