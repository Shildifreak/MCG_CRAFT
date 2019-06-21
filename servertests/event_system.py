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
