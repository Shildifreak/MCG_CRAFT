import sys, os
if __name__ == "__main__":
    sys.path.append(os.path.abspath("../.."))
    __package__ = "voxelengine.modules"
import collections.abc

class FrozenDict(collections.abc.Mapping):
	__slots__ = ("data")

	def __init__(self, *args, **kwargs):
		self.data = dict(*args, **kwargs)

	def __getitem__(self, key):
		return self.data.__getitem__(key)
	def __iter__(self):
		return self.data.__iter__()
	def __len__(self):
		return self.data.__len__()
	def __repr__(self):
		return self.data.__repr__()
	def __str__(self):
		return self.data.__str__()

	def __hash__(self):
		""" similar to tuple, frozendicts can have a hash if all their elements are hashable"""
		return hash(frozenset(self.items())) #may fail if it contains unhashable values like lists or other dictionaries

def freeze(obj):
	"""
	The freeze functions creates a hashable, immutable copy of an object.
	"""
	if isinstance(obj, (str, int, float, type(None), bool, frozenset, FrozenDict)):
		return obj
	if isinstance(obj, collections.abc.Sequence):
		return tuple(freeze(e) for e in obj)
	if isinstance(obj, set):
		return frozenset(obj)
	if isinstance(obj, collections.abc.Mapping):
		return FrozenDict({k:freeze(v) for k,v in obj.items()})
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
