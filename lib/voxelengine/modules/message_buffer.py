import collections, itertools


class MessageBuffer(object):
    """
    The Message Buffer is a smart drop-in upgrade for the player.outbox queue.
    It reschedules the order of messages to help create a more responsive gameplay,
    and it drops messages in favour of new more up to date messages.
    """
    def __init__(self):
        self.sentcount = 0 # number of msgs client requested
        
        self.goto_group       = MsgGroup(lambda _: True)
        self.entity_group     = MsgGroup(lambda m: m[1])
        self.vip_entity_group = MsgGroup(lambda m: m[1])
        self.block_group      = BlockGroup()
        self.hud_group        = MsgGroup(lambda m: m[1])
        self.type_group       = MsgGroup(lambda m: m[0])
        self.priority_group   = MsgGroup(lambda _: float("nan"))
        
        self.group_of = {"goto":(self.goto_group,),
                         "setentity":(self.entity_group,self.vip_entity_group),
                         "delentity":(self.entity_group,self.vip_entity_group),
                         "set":(self.block_group,), "delarea":(self.block_group,),
                         "clear":(self.priority_group,), "error":(self.priority_group,),
                         "focusdist":(self.type_group,), "focushud":(self.type_group,),
                         "sethud":(self.hud_group,), "delhud":(self.hud_group,),
                        }
        self.groups = (self.goto_group, self.entity_group, self.vip_entity_group, self.block_group,
                       self.hud_group, self.type_group) #priority_group is handled seperately
        self.groupcycler = itertools.cycle(self.groups)
        self.last_hit = self.groups[-1]

    def add(self,*message, priority = 0):
        """Entities have 2 Priority Levels (0: normal, 1: the player himself) for now"""
        message_type = message[0]
        group = self.group_of[message_type][priority]
        if message_type == "clear":
            self.block_group.clear()
            self.entity_group.clear()
            self.vip_entity_group.clear()
            self.goto_group.clear()
            self.barrier()
        group.add(message)
    
    def barrier(self):
        """make sure all currently buffered messages are output before any future messages"""
        msgs = tuple(self)
        for msg in msgs:
            self.priority_group.add(msg)
    
    def __iter__(self):
        # round robin
        yield from self.priority_group
        for group in self.groupcycler:
            msg = group.pop()
            if msg != None:
                self.last_hit = group
                self.sentcount += 1
                yield msg
            elif self.last_hit == group: #eine Runde rum ohne was zu finden
                break

class MsgGroup(object):
    def __init__(self, key):
        self.content = collections.OrderedDict()
        self.key = key
    def add(self, msg):
        k = self.key(msg)
        self.content[k] = msg
    def pop(self):
        if self.content:
            k, msg = self.content.popitem(last=False)
            return msg
        #return None
    def __iter__(self):
        while self.content:
            k, msg = self.content.popitem(last=False)
            yield msg
    def clear(self):
        self.content.clear()

class BlockGroup(object):
    """
    besides dropping replaced blocks, this BlockGroup should also
    combine set commands with the same block into setarea commands
    """
    def __init__(self):
        self.content = collections.OrderedDict()
        
    def add(self, message):
        position = message[1]
        self.content[position] = message

    def clear(self):
        self.content.clear()

    def pop(self):
        if self.content:
            k, msg = self.content.popitem(last=False)
            return msg
        # return None
