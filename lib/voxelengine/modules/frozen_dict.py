import sys, os
if __name__ == "__main__":
    sys.path.append(os.path.abspath("../.."))
    __package__ = "voxelengine.modules"
from voxelengine.modules.serializableCollections import Serializable

class FrozenDict(dict):
	__slots__ = ()

	def __hash__(self):
		""" similar to tuple, frozendicts can have a hash if all their elements are hashable"""
		return hash(frozenset(self.items())) #may fail if it contains unhashable values like lists or other dictionaries
		#except:
		#	return hash(frozenset(self.keys()))
		#	return 0 #makes all of them land in same bucket, so speed goes down to linear, but let's just hope there are not that many of this kind
	
	def _not_allowed(self, *args):
		raise AttributeError("'FrozenDict' object is immutable and therefore does not support this method")
	__setitem__ = _not_allowed
	__delitem__ = _not_allowed
	pop = _not_allowed
	popitem = _not_allowed
	setdefault = _not_allowed
	update = _not_allowed
	clear = _not_allowed

def freeze(obj):
	if isinstance(obj, (str, int, float, frozenset, FrozenDict)):
		return obj
	if isinstance(obj, (tuple, list)):
		return tuple(freeze(e) for e in obj)
	if isinstance(obj, set):
		return frozenset(obj)
	if isinstance(obj, dict):
		return FrozenDict({k:freeze(v) for k,v in obj.items()})
	if isinstance(obj, Serializable):
		return freeze(obj.__serialize__())
	raise ValueError("can't freeze object of type %s : %s" %(type(obj), obj))

if __name__ == "__main__":
	
	fd1 = freeze({"id":"STONE", "state":2})
	fd2 = freeze({"state":2, "id":"STONE"})
	fd3 = freeze({"id":["oh","no","a","list"]})
	print(fd1 == fd2)
	d = dict()
	d[fd1] = 1
	d[fd2] = 2
	d[fd3] = 3
	print(d)
