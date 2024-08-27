from collections import namedtuple, defaultdict
from voxelengine.modules.serializableCollections import Serializable

Event = namedtuple("Event", ("tag","area","data"))
Event.__new__.__defaults__ = (None,)
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

Observer = namedtuple("Observer", ["area", "tags", "handle_events"])

class EventSystem(Serializable):
	"""
	example event_tags:
		renderdistance # use for things like mob movement that should only occur when near players, or update of beacon blocks etc.
		block_update   # I don't know, maybe that's not specific enough, but for stuff like blocks being pushed, placed, broken, etc.
		redstone_update
		hitbox_update  # call for every entity and use for things like collision, pressure plates, ...
		explosion
		random_tick    # get's randomly created around players
		chat           # someone or something posted a chat message
	"""
	def __init__(self, world, event_queue_data):
		self.world = world
		self.observers = set()
		self.event_queue = EventQueue(event_queue_data) #[[event,...],...] #event queue sorted by remaining delay
	
	def __serialize__(self):
		return self.event_queue
	
	def add_event(self, event, delay=0):
		"""
		in <delay> ticks, 
		"""
		assert isinstance(event, Event)
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
			# find affected blocks and entities
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
				for observer in self.find_observers(event.area, event.tag):
					targets[observer].append(event)
			# update blocks
			changed_blocks = []
			with self.world.blocks.write_lock:
				for position, target_events in block_targets.items():
					block = self.world.blocks[position]
					changed = block.handle_events(target_events)
					assert isinstance(changed, bool) # handle_events has to return either True or False
					if changed:
						changed_blocks.append(block)
			for block in changed_blocks:
				block.save()
			# update entities
			for target, target_events in targets.items():
				target.handle_events(target_events)

	def tick(self):
		missed_events = self.event_queue.pop(0)
		assert not missed_events



	def find_observers(self, area, tags):
		""""""
		if isinstance(tags, str):
			tags = {tags} #M# could use frozenset instead
		for observer in self.observers:
			if observer.tags.issubset(tags):
				if observer.area.collides_with(area):
					yield observer

	def new_observer(self, callback, area, tags):
		if isinstance(tags, str):
			tags = frozenset((tags,))
		observer = Observer(area, tags, callback)
		self.observers.add(observer)
		return observer

	def del_observer(self, observer):
		self.observers.remove(observer)
