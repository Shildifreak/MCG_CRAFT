import collections, itertools
import _thread as thread
import threading
import time
import json
import codecs

from voxelengine.modules.message_buffer import MessageBuffer
from voxelengine.modules.shared import ACTIONS
from voxelengine.modules.geometry import Vector, Box, NOWHERE
from voxelengine.server.entities.entity import Entity

class Player(object):
	"""a player/observer is someone how looks through the eyes of an entity"""
	RENDERDISTANCE = 16
	def __init__(self,universe,initmessages=()):
		self.universe = universe
		self.entity = None
		self.world = None
		self.monitored_area = NOWHERE
		self.monitor_ticks = {0:0} # {m_id:gametick,...} gameticks when monitored area was changed 
		self.outbox = MessageBuffer()
		for msg in initmessages:
			self.outbox.add(*msg)
		self.focus_distance = 0
		self.action_states = {}
		self.was_pressed_set = set()
		self.was_released_set = set()
		self.new_chat_msgs_list = list()
		self.quit_flag = False
		
		self.hud_cache = {}
		
		self.DO_ASYNC_UPDATE = True
		self.area_updates = collections.OrderedDict()
		self.new_area_updates_event = threading.Event()
		if self.DO_ASYNC_UPDATE:
			thread.start_new_thread(self._update_area_loop, ())

	def quit(self):
		self.control(None)
		self.quit_flag = True

	def control(self,entity):
		if self.entity:
			if self.entity.get("is_tmp",False):
				self.entity.set_world(None,(0,0,0))
			else:
				#M# if player character, make invisible while offline?
				pass
		self.entity = entity
		self._notice_position()

	def create_character(self):
		world = self.universe.get_spawn_world()
		character = Entity()
		character.set_world(world,world.blocks.world_generator.spawnpoint)
		return character

	def is_pressed(self,key):
		"""return whether key is pressed """
		return self.action_states.get(key,False)

	def was_pressed(self,key):
		"""return whether key was pressed since last update"""
		return key in self.was_pressed_set

	def was_released(self,key):
		"""return whether key was released since last update"""
		return key in self.was_released_set

	def new_chat_messages(self):
		"""new messages that the player sent. Use like this:
		for msg in player.new_chat_messages():
			...
		"""
		while self.new_chat_msgs_list:
			yield self.new_chat_msgs_list.pop(0)

	def set_focus_distance(self,distance):
		"""Set maximum distance for focusing block"""
		self.outbox.add("focusdist","%g"%distance)
		self.focus_distance = distance

	def set_hud_text(self,element_id,text,position,rotation,size,alignment):
		text_b64 = codecs.encode(text.encode(), "base64").rstrip().decode()
		self.set_hud(element_id,"/"+text_b64,position,rotation,size,alignment)

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

	def _control_request(self, entity_id, password):
		for entity in itertools.chain(*(world.entities.entities for world in self.universe.worlds)):
			if entity.get("id",object()) == entity_id:
				if entity.get("password",object()) == password:
					break
				else:
					self.outbox.add("error", "Wrong password for controlling entity %s"%entity_id)
					return
		else:
			#M# if settings["auto_create_entities_for_players"]
			if entity_id.startswith("tmp:"):
				is_tmp = True
				entity_id = entity_id[4:]
			else:
				is_tmp = False
			entity = self.create_character()
			entity["id"] = entity_id
			entity["password"] = password
			entity["is_tmp"] = is_tmp
		self.control(entity)
		

	def _update_area(self, area, since_tick):
		"""when entering new world or walking around make sure to send list of modified blocks when compared to world at since_tick (use 0 for initial terrain generation)"""
		if since_tick != 0 and not self.world.blocks.block_storage.valid_history(since_tick):
			since_tick = 0
			self.outbox.add("delarea", area)
		# blocks
		block_adder = self.outbox.get_block_adder(area)
		if self.DO_ASYNC_UPDATE:
			old = self.area_updates.pop(repr(area), None) #M# hacky, think to make areas hashable
			if old:
				block_adder.close()
				block_adder = old[3]
				since_tick = old[2]
			self.area_updates[repr(area)] = (self.world, area, since_tick, block_adder) #M# is this thread save?
			self.new_area_updates_event.set()
			self.new_area_updates_event.clear()
		else:
			self._async_update_area(self.world, area, since_tick, block_adder)

	@staticmethod
	def _async_update_area(world, area, since_tick, block_adder, sleep=0):
		for position, block_client_version in world.blocks.list_changes(area, since_tick):
			block_adder.add("set", position, block_client_version)
			time.sleep(sleep)
		block_adder.close()
	
	def _update_area_loop(self):
		dt = 0.0001
		while not self.quit_flag:
			self.new_area_updates_event.wait()
			while self.area_updates:
				_, args = self.area_updates.popitem(last=False)
				self._async_update_area(*args,sleep=dt)
				time.sleep(dt)

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
			if self.entity:
				self.entity["rotation"] = (x,y)

		elif cmd == "keys" and len(args) == 1:
			action_states = int(args[0])
			for i,a in enumerate(ACTIONS):
				new_state = bool(action_states & (1<<(i)))
				if new_state and not self.is_pressed(a):
					self.was_pressed_set.add(a)
				if not new_state and self.is_pressed(a):
					self.was_released_set.add(a)
				self.action_states[a] = new_state

		elif cmd == "monitor" and len(args) == 7:
			x1,y1,z1, x2,y2,z2 = map(float, args[:6])
			m_id = int(args[6])
			previously_monitored_area = self.monitored_area
			self.monitored_area = Box(Vector(x1,y1,z1), Vector(x2,y2,z2))
			self.monitor_ticks[m_id] = self.world.clock.current_gametick # needed for partial update when resuming monitoring of some area
			# entities
			previous_entities = set(self.world.entities.find_entities(previously_monitored_area))
			new_entities = set(self.world.entities.find_entities(self.monitored_area))
			for entity in previous_entities - new_entities:
				self._del_entity(entity)
			for entity in new_entities - previous_entities:
				self._set_entity(entity)

		elif cmd == "update" and len(args) == 7:
			x1,y1,z1, x2,y2,z2 = map(float, args[:6])
			m_id = int(args[6])
			try:
				since_tick = self.monitor_ticks[m_id]
			except KeyError:
				since_tick = 0
				self.outbox.add("error", "unknown m_id",m_id)
			self._update_area(Box(Vector((x1,y1,z1)), Vector((x2,y2,z2))), since_tick)

		elif cmd == "control" and len(args) == 2:
			entity_id, password = args
			self._control_request(entity_id, password)

		elif cmd == "text" and len(args) >= 1:
			text = " ".join(args)
			self.new_chat_msgs_list.append(text)

		else:
			self.was_pressed_set.add(msg)

	def _notice_position(self):
		"""set position of camera/player"""
		if self.entity:
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
		self.monitored_area = NOWHERE
		generator_data = {	"name"   : self.world.blocks.world_generator.generator_data["name"],
							"seed"   : self.world.blocks.world_generator.generator_data["seed"],
							"code_js": self.world.blocks.world_generator.generator_data["code_js"]}
		self.outbox.add("clear",json.dumps(generator_data))

	def _set_entity(self,entity):
		priority = 1 if entity == self.entity else 0
		self.outbox.add("setentity",hash(entity),entity["texture"],entity["position"],*entity["rotation"], priority=priority)

	def _del_entity(self,entity):
		self.outbox.add("delentity",hash(entity))
