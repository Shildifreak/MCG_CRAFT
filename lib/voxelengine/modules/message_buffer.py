import collections, itertools, threading

class GotoGroup(object):
    def __init__(self):
        self.message = None
    def add(self, message):
        self.message = message
    def pop(self):
        m, self.message = self.message, None
        return m

class FifoGroup(collections.deque):
    add = collections.deque.append
    def pop(self):
        if self:
            return self.popleft()
        #return None

#class TellFifoGroup(FifoGroup):
#    def pop(self):
#        print len(self)
#        return FifoGroup.pop(self)

class EntityGroup(object):
    def __init__(self):
        self.content = collections.OrderedDict()
    def add(self,message):
        self.content[message[1]] = message
    def pop(self):
        if self.content:
            return self.content.popitem(last=False)[1]
        #return None

class MaskedBlockAdder(object):
    closed = False
    def __init__(self, block_group, area):
        self.block_group = block_group
        self.mask = BlockMask(area)
        self.block_group.add_mask(self.mask)
    def close(self):
        self.block_group.remove_mask(self.mask)
        self.closed = True
    def __del__(self):
        assert self.closed
    def add(self, *message):
        self.block_group.add(message, self.mask)

class BlockMask(object):
    def __init__(self, area):
        self.area = area
        self.masked_positions = set()
        self.masked_areas = []
    def add_masked_position(self, position):
        if position in self.area:
            self.masked_positions.add(position)
    def add_masked_area(self, area):
        if area.collides_with(self.area):
            self.masked_areas.append(area)
    def is_masked(self, position):
        assert position in self.area
        if position in self.masked_positions:
            return True
        for area in self.masked_areas:
            if position in area:
                return True
        return False

class BlockGroup(object):
    def __init__(self):
        self.serialized = []
        self.unserialized = collections.OrderedDict()
        self.chunksize = None
        self.masks = set()
        self._lock = threading.Lock()

    def add_mask(self, mask):
        with self._lock:
            self.masks.add(mask)
            print(len(self.masks),"masks")
    
    def remove_mask(self, mask):
        with self._lock:
            self.masks.remove(mask)
            print(len(self.masks),"masks")

    def add(self, message, mask=None):
        with self._lock:
            # block
            if message[0] in ("set","del"):
                position = message[1]
                if mask and mask.is_masked(position):
                    return
                # add message and update masks
                self.unserialized[position] = message
                for m in self.masks:
                    m.add_masked_position(position)

            elif message[0] in ("setarea","delarea"):
                area = message[1]
                if mask:
                    raise ValueError("setarea and delarea can't be masked")
                # serialize everything, add message and update masks
                self.serialized.extend(self.unserialized.values())
                self.unserialized.clear()
                self.serialized.append(message)
                for m in self.masks:
                    m.add_masked_area(area)

    def pop(self):
        if self.serialized:
            return self.serialized.pop(0)
        if self.unserialized:
            return self.unserialized.popitem(last=False)[1]
        # return None

class MessageBuffer(object):
    def __init__(self):
        self.sentcount = 0 # number of msgs client requested
        goto_group = GotoGroup()
        entity_group = EntityGroup()
        vip_entity_group = EntityGroup()
        self.block_group = block_group = BlockGroup()
        misc_group = FifoGroup()
        hud_group = FifoGroup()
        self.group_of = {"goto":(goto_group,),
                         "setentity":(entity_group,vip_entity_group), "delentity":(entity_group,vip_entity_group),
                         "set":(block_group,), "del":(block_group,), "setarea":(block_group,), "delarea":(block_group,), "clear":(block_group,),
                         "focusdist":(misc_group,), "setup":(misc_group,), "monitor_tick":(misc_group,), "error":(misc_group,),
                         "sethud":(hud_group,), "delhud":(hud_group,), "focushud":(hud_group,),
                        }
        self.groups = (misc_group, vip_entity_group, goto_group, hud_group, block_group, entity_group)
        self.groupcycler = itertools.cycle(self.groups)
        self.last_hit = self.groups[-1]

        self.msg_sources = {}

    def add(self,*message, priority = 0):
        """Entities have 2 Priority Levels (0: normal, 1: the player himself) for now"""
        group = self.group_of[message[0]][priority]
        group.add(message)
    
    def get_block_adder(self, area):
        """use block adder for asyncronous block adding"""
        return MaskedBlockAdder(self.block_group, area)

    def reset_msg_counter(self, count=0):
        """set how many messages client is currently willing to accept"""
        self.sentcount = count

    def __iter__(self):
        # round robin
        for group in self.groupcycler:
            msg = group.pop()
            if msg != None:
                yield " ".join(str(part) for part in msg)
                self.last_hit = group
                self.sentcount += 1
            elif self.last_hit == group: #eine Runde rum ohne was zu finden
                break
