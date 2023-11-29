import collections, itertools
import _thread as thread
import threading
import time
import base64
import hashlib

from voxelengine.modules.message_buffer import MessageBuffer
from voxelengine.modules.shared import ACTIONS
from voxelengine.modules.geometry import Vector, Box, NOWHERE
from voxelengine.server.entities.entity import Entity
from voxelengine.server.players.block_messenger import BlockMessenger

class Player(object):
	"""a player/observer is someone how looks through the eyes of an entity"""
	RENDERDISTANCE = 16
	CUSTOM_COMMANDS = set()
	def __init__(self,universe,initmessages=()):
		self.universe = universe
		self.entity = None
		self.world = None
		self.monitored_area = NOWHERE
		self.monitor_ticks = {0:0} # {m_id:gametick,...} gameticks when monitored area was changed 
		self.outbox = MessageBuffer()
		self.sendcount = 0 # acceptable number (remaining) of messages to send to client before next tick message
		for msg in initmessages:
			self.outbox.add(*msg)
		self.block_outbox = BlockMessenger(self.outbox)
		self.focus_distance = 0
		self.action_states = {}
		self.rotation = (0, 0)
		self.was_pressed_counter = collections.Counter()
		self.was_released_counter = collections.Counter()
		self.new_custom_commands_dict = collections.defaultdict(list)
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

	def is_pressed(self,key,threshold=0.5):
		"""return whether key is pressed """
		return self.get_pressure(key) >= threshold
	
	def get_pressure(self, key):
		"""return how much that key is pressed as a number between 0 and 1"""
		return self.action_states.get(key,0)

	def was_pressed(self,key):
		"""return number of times key was pressed since last update"""
		return self.was_pressed_counter[key]

	def was_released(self,key):
		"""return whether key was released since last update"""
		return self.was_released_counter[key]

	def new_chat_messages(self):
		"""new messages that the player sent. Use like this:
		for msg in player.new_chat_messages():
			...
		"""
		while self.new_chat_msgs_list:
			yield self.new_chat_msgs_list.pop(0)

	def set_focus_distance(self,distance):
		"""Set maximum distance for focusing block"""
		self.outbox.add("focusdist",distance)
		self.focus_distance = distance

	def set_hud_text(self,element_id,text,position,rotation,size,alignment):
		self.set_hud(element_id,"/"+text,position,rotation,size,alignment)

	def set_hud(self,element_id,texture,position,rotation,size,alignment):
		#if texture == "AIR":
		#	self.del_hud(element_id)
		#	return
		if self.hud_cache.get(element_id,None) == (texture,position,rotation,size,alignment):
			return
		self.outbox.add("sethud", element_id, texture, position, rotation, size, alignment)
		self.hud_cache[element_id] = (texture,position,rotation,size,alignment)

	def del_hud(self,element_id):
		if element_id in self.hud_cache:
			self.outbox.add("delhud", element_id)
			self.hud_cache.pop(element_id)

	def focus_hud(self):
		self.outbox.add("focushud")

	def handle_events(self, events):
		MUFFLED = ("random_tick")

		entity_events = collections.defaultdict(set) # {entity:tags}

		for event in events:
			if event.tag == "block_update":
				block = event.data
				position = block.position
				self.block_outbox.set(position, block.client_version())
			elif event.tag in ("entity_leave", "entity_enter", "entity_change"):
				entity = event.data
				entity_events[entity].add(event.tag)
			elif event.tag == "sound":
				sound_name = event.data
				position = event.area.center
				self.outbox.add("sound",sound_name, position)
			elif event.tag not in MUFFLED:
				print("player received",event.tag)

		for entity, tags in entity_events.items():
			if entity == self.entity and "entity_leave" in tags:
				self._notice_position()
			if "entity_leave" in tags and not "entity_enter" in tags:
				self._del_entity(entity)
			else:
				self._set_entity(entity)
				
	def autocomplete(self, msg):
		return ["test1","test2","test3"]

	### it follows a long list of private methods that make sure a player acts like one ###

	def _control_request(self, entity_id, password):
		password_hash = hashlib.sha256(password.encode()).hexdigest()
		del password
		for world in self.universe.worlds:
			entity = world.entities.get(entity_id, None)
			if entity is not None:
				if entity.get("password_hash",object()) == password_hash:
					break
				else:
					self.outbox.add("error", "Wrong password for controlling entity %s"%entity_id, True)
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
			entity["password_hash"] = password_hash
			entity["is_tmp"] = is_tmp
		self.control(entity)
		

	def _update_area(self, area, since_tick):
		"""when entering new world or walking around make sure to send list of modified blocks when compared to world at since_tick (use 0 for initial terrain generation)"""
		# blocks
		bookmark = self.block_outbox.acquire_bookmark()
		if self.DO_ASYNC_UPDATE:
			old = self.area_updates.pop(repr(area), None) #M# hacky, think to make areas hashable
			if old: # pending update exists
				self.block_outbox.release_bookmark(bookmark)
				bookmark = old[3]
				since_tick = old[2]
			self.area_updates[repr(area)] = (self.world, area, since_tick, bookmark) #M# is this thread save?
			self.new_area_updates_event.set()
			self.new_area_updates_event.clear()
		else:
			self._async_update_area(self.world, area, since_tick, bookmark)

	def _async_update_area(self, world, area, since_tick, bookmark, sleep=0):
		if since_tick != 0 and not world.blocks.block_storage.valid_history(since_tick):
			since_tick = 0
			self.block_outbox.delarea(area)
		for position, block_client_version in world.blocks.list_changes(area, since_tick):
			self.block_outbox.set(position, block_client_version, at_bookmark=bookmark)
			time.sleep(sleep)
		self.block_outbox.release_bookmark(bookmark)
	
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
		self.was_pressed_counter.clear()
		self.was_released_counter.clear()
		self.new_custom_commands_dict.clear()

	def _handle_input(self,msg):
		"""do something so is_pressed and was_pressed work"""
		if not isinstance(msg, collections.abc.Iterable):
			print("invalid msg format", msg, "all messages must be json arrays")
			return
		cmd, *args = msg

		def deep_type(obj):
			if isinstance(obj, (list, tuple)):
				return tuple(map(deep_type, obj))
			else:
				return type(obj)
		
		class Number(object):
			__slots__ = ()
			@staticmethod
			def __eq__(other):
				return other in (int, float)
		t_number = Number()
		t_vector = (t_number, t_number, t_number)
		
		argsformat = deep_type(args)

		if cmd == "tick" and argsformat == (int,):
			self.sendcount = args[0]

		elif cmd == "rot" and argsformat == ((t_number,t_number),):
			x,y = map(float,args[0])
			self.rotation = (x,y)

		elif cmd == "keys" and argsformat == (str,):
			action_states = base64.decodebytes(args[0].encode("ascii"))
			for i,a in enumerate(ACTIONS):
				new_state = int(action_states[i])/255.0 if (i < len(action_states)) else 0
				old_state = self.action_states.get(a,0)
				if new_state and not old_state:
					self.was_pressed_counter[a] += 1
				if not new_state and old_state:
					self.was_released_counter[a] += 1
				self.action_states[a] = new_state

		elif cmd == "monitor" and argsformat == (t_vector, t_vector, int):
			lower_bounds = Vector(map(float, args[0]))
			upper_bounds = Vector(map(float, args[1]))
			m_id = int(args[2])
			previously_monitored_area = self.monitored_area
			self.monitored_area = Box(lower_bounds, upper_bounds)
			self.monitor_ticks[m_id] = self.world.clock.current_gametick # needed for partial update when resuming monitoring of some area
			# entities
			previous_entities = set(self.world.entities.find_entities(previously_monitored_area))
			new_entities = set(self.world.entities.find_entities(self.monitored_area))
			for entity in previous_entities - new_entities:
				self._del_entity(entity)
			for entity in new_entities - previous_entities:
				self._set_entity(entity)

		elif cmd == "update" and argsformat == (t_vector, t_vector, int):
			lower_bounds = Vector(map(float, args[0]))
			upper_bounds = Vector(map(float, args[1]))
			m_id = int(args[2])
			try:
				since_tick = self.monitor_ticks[m_id]
			except KeyError:
				since_tick = 0
				self.outbox.add("error", "unknown m_id",m_id)
			self._update_area(Box(lower_bounds, upper_bounds), since_tick)

		elif cmd == "control" and argsformat == (str, str):
			entity_id, password = map(str, args)
			self._control_request(entity_id, password)

		elif cmd == "text" and argsformat == (str,):
			text = str(args[0])
			self.new_chat_msgs_list.append(text)

		elif cmd == "press" and argsformat == (str,):
			self.was_pressed_counter[str(args[0])] += 1
		
		elif cmd == "autocomplete" and argsformat == (str,):
			suggestions = self.autocomplete(args[0])
			self.outbox.add("textsuggestions",suggestions)
		
		elif cmd in self.CUSTOM_COMMANDS:
			self.new_custom_commands_dict[cmd].append(args)
		
		else:
			print("no matching format for message", msg, "with format", argsformat)

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
		self._clear()
	
	def _clear(self):
		# server side
		self.monitored_area = NOWHERE # stop monitoring area
		self.block_outbox.clear() # stop any still open bookmark from being used
		#self.area_updates.clear() # discard any still open area updates (wouldn't go through block_outbox now anyway)
		self.monitor_ticks = {0:0} # reset monitor ticks

		# client side
		generator_data = {	"name"   : self.world.blocks.world_generator.generator_data["name"],
							"seed"   : self.world.blocks.world_generator.generator_data["seed"],
							"code_js": self.world.blocks.world_generator.generator_data["code_js"]}
		self.outbox.add("clear",generator_data)
	
	def _set_entity(self,entity):
		priority = 1 if entity == self.entity else 0
		self.outbox.add("setentity",id(entity),entity["texture"],entity["position"],entity["rotation"],dict(entity["modelmaps"]), priority=priority)

	def _del_entity(self,entity):
		self.outbox.add("delentity",id(entity))
