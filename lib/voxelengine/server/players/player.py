import collections

from voxelengine.modules.message_buffer import MessageBuffer
from voxelengine.modules.shared import ACTIONS
from voxelengine.modules.geometry import Vector, Box

class Player(object):
	"""a player/observer is someone how looks through the eyes of an entity"""
	RENDERDISTANCE = 16
	def __init__(self,initmessages=()):
		self.entity = None
		self.world = None
		self.monitored_area = None #Box(Vector(-10,-10,-10),Vector(10,10,10))
		self.monitor_ticks = {0:0} # {m_id:gametick,...} gameticks when monitored area was changed 
		self.outbox = MessageBuffer()
		for msg in initmessages:
			self.outbox.add(*msg)
		self.focus_distance = 0
		self.action_states = {}
		self.was_pressed_set = set()
		self.was_released_set = set()
		self.quit_flag = False
		
		self.hud_cache = {}

	def quit(self):
		self.quit_flag = True
		if self.entity:
			self.entity.set_world(None,(0,0,0)) #M# maybe just change texture to ghost so player can rejoin later?

	def control(self,entity):
		self.entity = entity
		self._set_world(entity.world)
		self._notice_position()

	def is_pressed(self,key):
		"""return whether key is pressed """
		return self.action_states.get(key,False)

	def was_pressed(self,key):
		"""return whether key was pressed since last update"""
		return key in self.was_pressed_set

	def was_released(self,key):
		"""return whether key was released since last update"""
		return key in self.was_released_set

	def set_focus_distance(self,distance):
		"""Set maximum distance for focusing block"""
		self.outbox.add("focusdist","%g"%distance)
		self.focus_distance = distance

	def set_hud(self,element_id,texture,position,rotation,size,alignment):
		if texture == "AIR":
			self.del_hud(element_id)
			return
		if self.hud_cache.get(element_id,None) == (texture,position,rotation,size,alignment):
			return
		x,y,z = position; w,h = size
		self.outbox.add("sethud", element_id, texture, x, y, z, rotation, w, h, alignment)
		self.hud_cache[element_id] = (texture,position,rotation,size,alignment)

	def del_hud(self,element_id):
		if element_id in self.hud_cache:
			self.outbox.add("delhud", element_id)
			self.hud_cache.pop(element_id)

	def focus_hud(self):
		self.outbox.add("focushud")

	def handle_events(self, events):
		entity_events = collections.defaultdict(set) # {entity:tags}

		for event in events:
			if event.tag == "block_update":
				block = event.data
				position = block.position
				self.outbox.add("set", position, block.client_version())
			elif event.tag in ("entity_leave", "entity_enter", "entity_change"):
				entity = event.data
				entity_events[entity].add(event.tag)
			elif event.tag in "entity_enter":
				entity = event.data
				entity_movements[entity] = "move"
			else:
				print("player received",event.tag)

		for entity, tags in entity_events.items():
			if entity == self.entity and "entity_leave" in tags:
				self._notice_position()
			if "entity_leave" in tags and not "entity_enter" in tags:
				self._del_entity(entity)
			else:
				self._set_entity(entity)
				

	### it follows a long list of private methods that make sure a player acts like one ###

	def _update_area(self, area, since_tick):
		"""when entering new world or walking around make sure to send list of modified blocks when compared to world at since_tick (use 0 for initial terrain generation)"""
		if since_tick != 0 and not self.world.blocks.block_storage.valid_history(since_tick):
			since_tick = 0
			self.outbox.add("delarea", area)
		for position, block in self.world.blocks.list_changes(area, since_tick):
			self.outbox.add("set", position, block.client_version())
		# chunksize, all blocks in radius, etc
		# if since tick is not available send clear_area first

	def _update(self):
		"""internal update method, automatically called by game loop"""
		self.was_pressed_set.clear()
		self.was_released_set.clear()

	def _handle_input(self,msg):
		"""do something so is_pressed and was_pressed work"""
		cmd, *args = msg.split(" ")

		if cmd == "tick" and len(args) == 1:
			self.outbox.reset_msg_counter(-int(args[0]))

		elif cmd == "rot" and len(args) == 2:
			x,y = map(float,args)
			self.entity["rotation"] = (x,y)

		elif cmd == "keys" and len(args) == 1:
			action_states = int(args[0])
			for i,a in enumerate(ACTIONS):
				new_state = bool(action_states & (1<<(i+1)))
				if new_state and not self.is_pressed(a):
					self.was_pressed_set.add(a)
				if not new_state and self.is_pressed(a):
					self.was_released_set.add(a)
				self.action_states[a] = new_state

		elif cmd == "monitor" and len(args) == 7:
			x1,y1,z1, x2,y2,z2 = map(float, args[:6])
			m_id = int(args[6])
			self.monitored_area = Box(Vector(x1,y1,z1), Vector(x2,y2,z2))
			self.monitor_ticks[m_id] = self.world.clock.current_gametick # needed for partial update when resuming monitoring of some area

		elif cmd == "update" and len(args) == 7:
			x1,y1,z1, x2,y2,z2 = map(float, args[:6])
			m_id = int(args[6])
			try:
				since_tick = self.monitor_ticks[m_id]
			except KeyError:
				since_tick = 0
				self.outbox.add("error", "unknown m_id",m_id)
			self._update_area(Box(Vector((x1,y1,z1)), Vector((x2,y2,z2))), since_tick)

		else:
			self.was_pressed_set.add(msg)

	def _notice_position(self):
		"""set position of camera/player"""
		if self.entity["position"]:
			if self.entity.world != self.world:
				self._set_world(self.entity.world)
			self.outbox.add("goto",self.entity["position"])

	def _set_world(self, new_world):
		"""to be called when self.entity.world has changed """
		if self.world:
			self.world.players.remove(self)
		if new_world:
			new_world.players.add(self)
		self.world = new_world
		self.monitored_area = None
		self.outbox.add("clear")

	def _set_entity(self,entity):
		priority = 1 if entity == self.entity else 0
		self.outbox.add("setentity",hash(entity),entity["texture"],entity["position"],*entity["rotation"], priority=priority)

	def _del_entity(self,entity):
		self.outbox.add("delentity",hash(entity))
