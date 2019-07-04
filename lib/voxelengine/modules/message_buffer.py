import collections

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

class BlockGroup(object):
    def __init__(self):
        self.serialized = []
        self.unserialized = collections.OrderedDict()
        self.chunksize = None
    def add(self,message):
        if message[0] == "chunksize":
            self.chunksize = message[1]
        # only optimize when chunksize is known
        if self.chunksize:
            # area
            if message[0] in ("setarea","delarea"):
                chunkposition = message[1]
                self.unserialized = collections.OrderedDict((k,v) for k,v in self.unserialized.iteritems() if not self.in_chunk(message,chunkposition))
                self.unserialized[("chunk",chunkposition)] = message
                return
            # block
            if message[0] in ("set","del"):
                blockposition = message[1]
                self.unserialized[("block",blockposition)] = message
                return
        # default: serialize everything
        self.serialized.extend(self.unserialized.values())
        self.unserialized.clear()
        self.serialized.append(message)
    def pop(self):
        if self.serialized:
            return self.serialized.pop(0)
        if self.unserialized:
            return self.unserialized.popitem(last=False)[1]
        # return None
    @staticmethod
    def in_chunk(message, chunkposition):
        if message[0] in ("set","del"):
            blockposition = message[1]
            return (blockposition >> self.chunksize) == chunkposition
        else:
            return False
            
            
            
class MessageBuffer(object):
    def __init__(self):
        self.sentcount = 0 # number of msgs client requested
        goto_group = GotoGroup()
        entity_group = EntityGroup()
        vip_entity_group = EntityGroup()
        block_group = BlockGroup()
        misc_group = FifoGroup()
        hud_group = FifoGroup()
        self.group_of = {"goto":(goto_group,),
                         "setentity":(entity_group,vip_entity_group), "delentity":(entity_group,vip_entity_group),
                         "set":(block_group,), "del":(block_group,), "setarea":(block_group,), "delarea":(block_group,), "clear":(block_group,), "chunksize":(block_group,),
                         "focusdist":(misc_group,), "setup":(misc_group,),
                         "sethud":(hud_group,), "delhud":(hud_group,), "focushud":(hud_group,),
                        }
        self.groups = (misc_group, vip_entity_group, goto_group, hud_group, block_group, entity_group)
        self.groupcycler = itertools.cycle(self.groups)
        self.last_hit = self.groups[-1]

    def add(self,*message,**args): #M# cause named after * doesn't work in python2.x
        """Entities have 2 Priority Levels (0: normal, 1: the player himself) for now"""
        priority = args.get("priority",0)
        group = self.group_of[message[0]][priority]
        group.add(message)

    def reset_msg_counter(self, count=0):
        """set how many messages client is currently willing to accept"""
        self.sentcount = count

    def __iter__(self):
        # round robin
        for group in groupcycler:
            msg = group.pop()
            if msg != None:
                yield " ".join(str(part) for part in msg)
                self.last_hit = group
                self.sentcount += 1
            elif self.last_hit == group: #eine Runde rum ohne was zu finden
                break
