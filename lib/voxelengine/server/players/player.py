from voxelengine.modules.message_buffer import MessageBuffer
from voxelengine.modules.shared import ACTIONS

class Player(object):
	"""a player/observer is someone how looks through the eyes of an entity"""
	RENDERDISTANCE = 16
	def __init__(self,initmessages=()):
		self.entity = None
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
		if self.entity:
			old_world = self.entity.world
		else:
			old_world = None
		self.entity = entity

		self._notice_world(old_world,entity.world)
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

	def get_focused_pos(self,max_distance=None):
		"""Line of sight search from current position. If a block is
		intersected it's position is returned, along with the face and distance:
			(distance, position, face)
		If no block is found, return (None, None, None).

		max_distance : How many blocks away to search for a hit.
		""" 
		if max_distance == None:
			max_distance = self.focus_distance
		return hit_test(lambda v:self.entity.world.get_block(v)["id"]!="AIR",self.entity["position"],
						self.entity.get_sight_vector(),max_distance)
	
	def get_focused_entity(self,max_distance=None):
		#M# to be moved to entity!
		"""Line of sight search from current position. If an entity is
		intersected it is returned, along with the distance.
		If no block is found, return (None, None).

		max_distance : How many blocks away to search for a hit."""
		if max_distance == None:
			max_distance = self.focus_distance
		nearest_entity = None
		ray = Ray(self.entity["position"],self.entity.get_sight_vector())
		for entity in self.entity.world.get_entities(): #M# limit considered entities
			if entity is self.entity:
				continue
			d = entity.HITBOX.raytest(entity["position"],ray)
			if (d != False) and (d < max_distance):
				nearest_entity = entity
				max_distance = d
		if nearest_entity:
			return max_distance, nearest_entity
		return (None, None)

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
		for event in events:
			print("player received:",event.tag)
			if event.tag == "block_update":
				block = event.data
				position = block.position
				self.outbox.add("set", position, block.client_version())

	### it follows a long list of private methods that make sure a player acts like one ###

	def _update_monitored_area(self, area, since_tick):
		"""when entering new world or walking around make sure to send list of modified blocks when compared to world at since_tick (use 0 for initial terrain generation)"""
		raise NotImplementedError()
		# chunksize, all blocks in radius, etc

	def _update(self):
		"""internal update method, automatically called by game loop"""
		self.was_pressed_set.clear()
		self.was_released_set.clear()

	def _handle_input(self,msg):
		"""do something so is_pressed and was_pressed work"""
		if msg.startswith("tick"):
			self.outbox.reset_msg_counter(-int(msg.split(" ")[1]))
		elif msg.startswith("rot"):
			x,y = map(float,msg.split(" ")[1:])
			self.entity["rotation"] = (x,y)
		elif msg.startswith("keys"):
			action_states = int(msg.split(" ")[1])
			for i,a in enumerate(ACTIONS):
				new_state = bool(action_states & (1<<(i+1)))
				if new_state and not self.is_pressed(a):
					self.was_pressed_set.add(a)
				if not new_state and self.is_pressed(a):
					self.was_released_set.add(a)
				self.action_states[a] = new_state
		elif msg.startswith("monitor"):
			x1,y1,z1, x2,y2,z2, since_tick = map(int, msg.split(" ")[1:])
			self._update_monitored_area(Box(Vector((x1,y1,z1)), Vector((x2,y2,z2))), since_tick)
		else:
			self.was_pressed_set.add(msg)

	def _notice_position(self):
		"""set position of camera/player"""
		if self.entity["position"]:
			self.outbox.add("goto",*self.entity["position"])

	def _notice_world(self, old_world, new_world):
		"""to be called when self.entity.world has changed """
		if old_world:
			old_world.players.discard(self)
		if new_world:
			new_world.players.add(self)
		self.outbox.add("clear")

	def _set_entity(self,entity):
		priority = 1 if entity == self.entity else 0
		self.outbox.add("setentity",hash(entity),entity["texture"],entity["position"],*entity["rotation"], priority=priority)

	def _del_entity(self,entity):
		self.outbox.add("delentity",hash(entity))
