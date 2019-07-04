class EntityWorld(object):
	def find_entity(self, area, tag):
		"""entities may be different in size in regards to different tags"""
        #entities are added into binary box tree by their binary box cover[s] for the corresponding tags
        #when searching build a set of all possibly affected entities
        #then do a real test on the hitboxes



class Entity(ObservableDict):
    def __init__(self,data = None):
        ObservableDict.__init__(self,data if data != None else {})
        self.world = None
        self.observers = set()
        self.old_chunk_observers = set()

        self.setdefault("position",(0,0,0))
        self.setdefault("rotation",(0,0))
        self.setdefault("texture",0)
        self.setdefault("speed",5)

        self.register_item_callback(self._on_position_change,"position")
        self.register_item_callback(self._notify_chunk_observers,"rotation")
        self.register_item_callback(self._notify_chunk_observers,"texture")
        self.register_item_sanitizer(lambda pos: Vector(pos),"position")

    def _on_position_change(self, new_position):
        """set position of entity"""
        # stuff so other players can see me move
        new_chunk_observers = self.world._get_chunk(new_position).observers if self.world and new_position else set()
        for o in self.old_chunk_observers.difference(new_chunk_observers):         # tell everyone who doesn't also observe the new position that I'm gone
            o._del_entity(self)
        for o in new_chunk_observers:        # tell everyone who is observing the new position that I'm now here
            o._set_entity(self)
        self.old_chunk_observers = new_chunk_observers
        
        # stuff so own players move
        for observer in self.observers:
            observer._notice_position()

    def set_world(self, new_world, new_position):
        """ adjust to new world """
        # savely remove from old world
        old_world = self.world
        if old_world:
            self.world.entities.discard(self)
        # add to new world:
        self.world = new_world
        if new_world:
            new_world.entities.add(self)
        self["position"] = new_position
        for observer in self.observers:
            observer._notice_world(old_world,new_world)
        
    def get_sight_vector(self):
        """ Returns the current line of sight vector indicating the direction
        the entity is looking.

        """
        x, y = self["rotation"]
        # y ranges from -90 to 90, or -pi/2 to pi/2, so m ranges from 0 to 1 and
        # is 1 when looking ahead parallel to the ground and 0 when looking
        # straight up or down.
        m = math.cos(math.radians(y))
        # dy ranges from -1 to 1 and is -1 when looking straight down and 1 when
        # looking straight up.
        dy = math.sin(math.radians(y))
        dx = math.cos(math.radians(x - 90)) * m
        dz = math.sin(math.radians(x - 90)) * m
        return Vector((dx, dy, dz))

    def _notify_chunk_observers(self,*_):
        if self.world:
            for observer in self.world._get_chunk(self["position"]).observers:
                observer._set_entity(self)

                

class Player(object):
    """a player/observer is someone how looks through the eyes of an entity"""
    RENDERDISTANCE = 16
    def __init__(self,renderlimit,initmessages=()):
        self.renderlimit = renderlimit
        self.entity = None
        self.outbox = MessageBuffer()
        for msg in initmessages:
            self.outbox.add(*msg)
        self.focus_distance = 0
        self.action_states = {}
        self.was_pressed_set = set()
        self.was_released_set = set()
        self.observed_chunks = set()
        self._lc = set() #load chunks
        self._uc = set() #unload chunks
        if self.renderlimit:
            thread.start_new_thread(self._update_chunks_loop,())
        self.quit_flag = False
        self.lock = thread.allocate_lock() # lock this while making changes to entity, observed_chunks, _lc, _uc
        self.lock_used = False             # and activate this to tell update_chunks_loop to dismiss changes
        
        self.hud_cache = {}

    def quit(self):
        self.quit_flag = True
        if self.entity:
            self.entity.set_world(None,(0,0,0)) #M# maybe just change texture to ghost so player can rejoin later?

    def observe(self,entity):
        self.lock.acquire()
        if self.entity:
            self.entity.observers.remove(self)
            old_world = self.entity.world
        else:
            old_world = None
        self.entity = entity
        entity.observers.add(self)
        self.lock_used = True
        self.lock.release()

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

    # DEPRECATED
    #def is_active(self):
    #    """indicates whether client responds (fast enough)"""
    #    return self.sentcount >= 0

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

    ### it follows a long list of private methods that make sure a player acts like one ###

    def _init_chunks(self):
        if not self.entity or not self.entity.world:
            return
        for chunk in self.entity.world.chunks.values():
            self._lc.add(chunk)
        if self.lock.acquire():
            self._lc = sorted(self._lc,key=self._chunk_priority_func,reverse=True)
            self.lock.release()
        else:
            print "locking error"

    def _update_chunks_loop(self):
        try:
            while True:
                self.lock_used = False
                # copy some attributes because function is used asynchron
                try:
                    while not self.entity or not self.entity.world:
                        time.sleep(0.1)
                    world = self.entity.world
                    position = self.entity["position"].normalize()
                    radius=self.RENDERDISTANCE
                    r = range(-radius,radius,1<<world.chunksize)+[radius]
                    chunks = set()
                    for dx in r:
                        for dy in r:
                            time.sleep(0.01)
                            for dz in r:
                                chunkpos = position+(dx,dy,dz)
                                chunk = world._get_chunk(chunkpos,load_on_miss = not DOASYNCLOAD)
                                if chunk == None:
                                    world._async_load_chunk(chunkpos)
                                elif chunk == "loading":
                                    pass
                                else:
                                    chunks.add(chunk)
                except:
                    if self.lock_used:
                        continue
                    else:
                        raise
                #M# don't do any unloads, because who needs them anyway I mean... do them if they are too far away
                uc = {} #self.observed_chunks.difference(chunks)
                lc = chunks.difference(self.observed_chunks)
                lc = sorted(lc,key=self._chunk_priority_func,reverse=True)
                if self.lock.acquire(False):
                    if not self.lock_used:
                        self._uc = uc
                        self._lc = lc
                    self.lock.release()
        except Exception as e:
            if "-debug" in sys.argv or not self.quit_flag:
                raise e

    def _update_chunks(self):
        # unload chunks
        if self._uc:
            chunk = self._uc.pop()
            if chunk in self.observed_chunks:
                self.observed_chunks.remove(chunk)
                chunk.observers.remove(self)
                self.outbox.add("delarea",chunk.position)
                for entity in chunk.get_entities():
                    self._del_entity(entity)
        # load chunks
        if self._lc:
            chunk = self._lc.pop()
            if not chunk in self.observed_chunks and chunk.is_fully_generated():
                self.observed_chunks.add(chunk)
                codec = [b.client_version() for b in chunk.block_codec]
                data = repr((codec,chunk.compressed_data))
                self.outbox.add("setarea",chunk.position,data)
                chunk.observers.add(self)
                for entity in chunk.get_entities():
                    self._set_entity(entity)

    def _chunk_priority_func(self,chunk):
        return self._priority_func(chunk.position<<chunk.chunksize)

    def _priority_func(self,position):
        dist = position+(Vector([1,1,1])<<(self.entity.world.chunksize-1))-self.entity["position"]
        return sum(map(abs,dist))

    def _update(self):
        """internal update method, automatically called by game loop"""
        self._update_chunks()
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
        else:
            self.was_pressed_set.add(msg)

    def _notice_position(self):
        """set position of camera/player"""
        if self.entity["position"]:
            self.outbox.add("goto",*self.entity["position"])

    def _notice_world(self, old_world, new_world):
        """to be called when self.entity.world has changed """
        self.lock.acquire()
        if old_world:
            old_world.players.discard(self)
        for chunk in self.observed_chunks:
            chunk.observers.remove(self)
        self.observed_chunks.clear()
        self.outbox.add("clear")
        if new_world:
            new_world.players.add(self)
            self.outbox.add("chunksize", new_world.chunksize) #M# is that right here? Make sure it doesn't get reordered with setting of blocks
        self.lock_used = True
        self.lock.release()
        if not self.renderlimit:
            self._init_chunks()

        
    def _notice_block(self,position,block_data):
        """send blockinformation to client"""
        self.outbox.add("set", position, block_data.client_version())

    def _notice_new_chunk(self,chunk):
        if not self.renderlimit:
            if chunk not in self._lc:
                self._lc.append(chunk)

    def _set_entity(self,entity):
        priority = 1 if entity == self.entity else 0
        self.outbox.add("setentity",hash(entity),entity["texture"],entity["position"],*entity["rotation"], priority=priority)

    def _del_entity(self,entity):
        self.outbox.add("delentity",hash(entity))
