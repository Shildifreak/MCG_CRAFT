import collections, threading

class BlockMessenger(object):
    """
    maintain bookmarks to allow for threaded block message insertion
    with this block messages can be added as if done so at the time of bookmark creation
    """
    def __init__(self, message_buffer):
        self.message_buffer = message_buffer
        
        self.dirty_positions = collections.OrderedDict() # {position: max_bookmark at time of insertion,...}
        self.bookmarks = collections.Counter() # {bookmark_id: reference_counter,...}
        self.max_bookmark = 0
        self.set_since_last_bookmark = False
        self.last_clear = 0
        
        self._lock = threading.Lock()

    def acquire_bookmark(self):
        assert len(self.bookmarks) < 10 # set this high enough to work but low enough to catch memory leaks
        with self._lock:
            if not self.set_since_last_bookmark:
                bookmark = self.bookmarks[self.max_bookmark]
            else:
                self.max_bookmark += 1
                bookmark = self.max_bookmark
            self.bookmarks[bookmark] += 1
            self.set_since_last_bookmark = False
            print(len(self.bookmarks))
            return bookmark

    def release_bookmark(self, bookmark):
        with self._lock:
            if self.bookmarks[bookmark] > 1:
                self.bookmarks[bookmark] -= 1
            else:
                del self.bookmarks[bookmark]
                print(len(self.bookmarks))
                # remove all dirty positions older than first bookmark
                if self.bookmarks:
                    min_bookmark = min(self.bookmarks)
                    while len(self.dirty_positions) and (next(iter(self.dirty_positions))[1] < min_bookmark):
                        # pop position
                        self.dirty_positions.popitem(last=False)
                else:
                    self.dirty_positions.clear()

    def set(self, position, block, at_bookmark=None):
        with self._lock:
            # abort if position changed since bookmark
            if at_bookmark:
                last_changed = self.dirty_positions.get(position, self.last_clear)
                if at_bookmark <= last_changed:
                    return
            else:
                at_bookmark = self.max_bookmark + 1
            # add message and update masks
            self.message_buffer.add("set", position, block)
            # update dirty_positions
            if self.bookmarks: #otherwise no one will be interested anyway
                self.set_since_last_bookmark = True
                self.dirty_positions[position] = at_bookmark - 1
                self.dirty_positions.move_to_end(position)
    
    def delarea(self):
        raise NotImplementedError()
        self.message_buffer.add("delarea",area)
    
    def clear(self):
        with self._lock:
            self.dirty_positions.clear()
            self.last_clear = self.max_bookmark

#class PositionIndexedSet(object):
#    def __init__(self):
#        #self.data = set()
#        self.index = collections.defaultdict(set)
#        self.counter = collections.Counter()
#    def add(self, mask):
#        for bb in mask.area.binary_box_cover():
#            self.index[bb].add(mask)
#            self.counter[bb.scale] += 1
#    def remove(self, mask):
#        for bb in mask.area.binary_box_cover():
#            self.index[bb].remove(mask)
#            if self.index[bb] == set():
#                del self.index[bb]
#            self.counter[bb.scale] -= 1
#            if self.counter[bb.scale] <= 0:
#                del self.counter[bb.scale]
#    def at_position(self, position):
#        masks = set()
#        for scale in self.counter.keys():
#            bb = BinaryBox(scale, position >> scale)
#            masks.update(self.index[bb])
#        return masks
#    def __len__(self):
#        return sum(self.counter.values())
