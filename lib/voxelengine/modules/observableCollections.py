# data that should be representable: containers: dicts, lists; literals: ints, floats, strings
# should be able to subscribe to each of them to be noticed of changes
# should be possible to move stuff (observer move with it) and copy stuff (observers stay where they are)
# when something is changed that implies that all parents have to call their callbacks as well

import sys, os
if __name__ == "__main__":
    sys.path.append(os.path.abspath("../.."))
    print(sys.path)
    __package__ = "voxelengine.modules"

import collections, itertools
from voxelengine.modules.serializableCollections import Serializable

def observable_from(data):
    if isinstance(data, Observable):
        raise ValueError("is already Observable") #there are multiple ways to deal with parent / sanitizers / items can't be copied only moved / ... so do this outside
    if isinstance(data, collections.abc.MutableMapping):
        return ObservableDict(data)
    if isinstance(data, collections.abc.MutableSequence):
        return ObservableList(data)
    return data

class Observable(Serializable):
    __slots__ = ("parent","parent_key","item_callbacks","callbacks","sanitizers","default_sanitizer","data","static_keys")
    def __init__(self, data, static_keys):
        self.parent = None
        self.parent_key = None
        self.item_callbacks = collections.defaultdict(set)
        self.callbacks = set()
        self.sanitizers = dict()
        self.default_sanitizer = lambda x:x
        self.data = data
        self.static_keys = static_keys

    def __serialize__(self):
        return self.data
    
    def __len__(self):
        return len(self.data)

    def __getitem__(self,key):
        return self.data[key]

    def __iter__(self):
        return iter(self.data)

    def get(self, key, default=None):
        try:
            return self.data[key]
        except (KeyError,IndexError):
            return default

    def _adopted_value(self,value,static_key=None):
        value = self.sanitizers.get(static_key,self.default_sanitizer)(value)
        if not isinstance(value,Observable):
            value = observable_from(value)
        if isinstance(value,Observable):
            assert value.parent == None
            value.parent = self
            value.parent_key = static_key
        return value

    def __setitem__(self,key,value):
        prev_value = self.get(key,None)
        if isinstance(prev_value, Observable):
            prev_value.parent = None
        static_key = key if self.static_keys else None
        value = self._adopted_value(value,static_key)
        self.data[key] = value
        self.trigger(static_key)
    
    def __delitem__(self,key):
        raise NotImplementedError()

    def replace(self,key,value):
        prev_value = self[key]
        self[key] = value #should cause trigger
        return prev_value

    def register_callback(self,callback,initial_call=True):
        self.callbacks.add(callback)
        if initial_call:
            callback(self)

    def unregister_callback(self,callback):
        self.callbacks.remove(callback)

    def register_item_callback(self,callback,key,initial_call=True):
        self.item_callbacks[key].add(callback)
        if initial_call:
            callback(self[key])

    def unregister_item_callback(self,callback,key):
        self.item_callbacks[key].remove(callback)

    def register_item_sanitizer(self,sanitizer,key,initial_call=True):
        self.sanitizers[key] = sanitizer
        if initial_call:
            try:
                value = self[key]
            except (KeyError, IndexError):
                pass
            else:
                self[key] = value #will be sanitized by reassignment now that sanitizer is in place

    def register_default_item_sanitizer(self, sanitizer, initial_call=True):
        self.default_sanitizer = sanitizer
        if initial_call:
            for key in self.keys():
                self[key] = self[key]

    def trigger(self,key):
        for callback in self.item_callbacks[key]:
            callback(self.get(key))
        for callback in self.callbacks:
            callback(self)
        if self.parent:
            self.parent.trigger(self.parent_key)

    def copy(self):
        raise NotImplementedError()

    def may_contain(self, item):
        #M# todo: test for inception
        return True

    __hash__ = object.__hash__
    __eq__ = object.__eq__

class ObservableDict(Observable, collections.abc.MutableMapping):
    __slots__ = ()
    def __init__(self,data={}):
        super().__init__(data={}, static_keys=True)
        self.dict_update(data)

    def dict_update(self,data):
        assert not isinstance(data, Observable)
        for key in data:
            self[key] = data[key]

    def setdefault(self, key, value):
        if key not in self.data:
            self[key] = value
        return self[key]
    
    def keys(self):
        return self.data.keys()

class ObservableList(Observable, collections.abc.MutableSequence):
    __slots__ = ()
    def __init__(self,data=[]):
        super().__init__(data=[], static_keys=False)
        self.extend(data)

    def extend(self,values):
        assert not isinstance(values, Observable)
        self.data.extend(map(self._adopted_value,values))
        self.trigger(None)

    def append(self,value):
        self.data.append(self._adopted_value(value))
        self.trigger(None)

    def insert(self,index,value):
        self.data.insert(index,self._adopted_value(value))
        self.trigger(None)

    def pop(self,index):
        value = self.data.pop(index)
        if isinstance(value, Observable):
            value.parent = None
        self.trigger(None)
        return value

    def count(self,*args,**kwargs):
        return self.data.count(*args,**kwargs)
    
    def index(self,*args,**kwargs):
        return self.data.index(*args,**kwargs)
    
    def remove(self, value):
        self.pop(self.index(value))

    def keys(self):
        return range(len(self.data))

if __name__ == "__main__":
    f = observable_from
    test = observable_from({"a":{"b":1}})
    observable_from(test)
    
#    root = observable_from({"a":7,"b":[1,2,3]})
#    root.setdefault("c",[4])
#    root["c"].append(2)
#    root["c"].remove(4)
#    print(type(root["c"]), root["c"])
#    a = observable_from({1:2})
#    b = observable_from({1:2})
#
#    print("----")
#    x = observable_from({"test":[1,2,3]})
#    dict_containing_child_of_other_observable = {"aha": x["test"]}
#    try:
#        y = observable_from(dict_containing_child_of_other_observable)
#    except ValueError as e:
#        print("Expected Error:", e)
