from collections import namedtuple, defaultdict

Event = namedtuple("Event", ("tag","area","data"))
Event.__doc__ += """
search for entities and blocks in <area> that registered for <event_tag> and call them back with event_data"""

class EventQueue(list):
	def __getitem__(self, index):
		while len(self) <= index:
			self.append([])
		return super(EventQueue,self).__getitem__(index)
	def pop(self, index):
		if len(self) <= index:
			return []
		return super(EventQueue,self).pop(index)

class EventSystem(object):
	"""
	example event_tags:
		renderdistance # use for things like mob movement that should only occur when near players, or update of beacon blocks etc.
		block_update   # I don't know, maybe that's not specific enough, but for stuff like blocks being pushed, placed, broken, etc.
		redstone_update
		hitbox_update  # call for every entity and use for things like collision, pressure plates, ...
		explosion
		random_tick    # get's randomly created around players
	"""
	def __init__(self, world, event_data):
		self.world = world
		if event_data:
			raise NotImplementedError()

		self.event_queue = EventQueue() #[[event,...],...] #event queue sorted by remaining delay
	
	def add_event(self, delay, event):
		"""
		in <delay> ticks, 
		"""
		assert delay >= 0
		self.event_queue[delay].append(event)
	
	def clear_events(self):
		self.event_queue.clear()
	
	def process_events(self):
		if self.event_queue:
			events = self.event_queue[0]
		else:
			events = ()
		while events:
			targets = defaultdict(list)
			block_targets = defaultdict(list)
			while events:
				event = events.pop(0)
				for position in self.world.blocks.block_world_index.find_blocks(event.area, event.tag):
					block_targets[position].append(event)
				for entity in self.world.entities.find_entities(event.area, event.tag):
					targets[entity].append(event)
				for player in self.world.players.find_players(event.area, event.tag):
					targets[player].append(event)
			for position, target_events in block_targets.items():
				targets[self.world.blocks[position]] = target_events
			for target, target_events in targets.items():
				target.handle_events(target_events)

	def tick(self):
		missed_events = self.event_queue.pop(0)
		assert not missed_events
