
import bisect
import itertools

import rtree.index

ID = 0

class BinaryDict(object):
	
	def __init__(self,data=(),dimension=3):
		self.data = dict(data)
		p = rtree.index.Property()
		p.dimension = dimension
		self.index = rtree.index.Index(properties=p)
	
	def __getitem__(self, position):
		return self.data[position]
	
	def __setitem__(self, position, value):
		coordinates = (*position,*position)
		self.index.delete(ID,coordinates)
		self.index.add(ID,coordinates,value)

		self.data[position] = value
	
	def __delitem__(self, position):
		coordinates = (*position,*position)
		self.index.delete(ID,coordinates)

		del self.data[position]
	
	def setdefault(self, position, value):
		coordinates = (*position,*position)
		self.index.delete(ID,coordinates)
		self.index.add(ID,coordinates,value)
		
		return self.data.setdefault(position, value)
	
	def pop(self, position):
		coordinates = (*position,*position)
		self.index.delete(ID,coordinates)

		return self.data.pop(position)
	
	def items(self):
		return self.data.items()
	
	def __repr__(self):
		return repr(self.data)
	
	def __len__(self):
		return len(self.data)

	def list_blocks_in_binary_box(self, binary_box):
		"""return all blocks that are in binary_box"""
		bounding_box = binary_box.bounding_box()
		coordinates = (*bounding_box.lower_bounds, *bounding_box.upper_bounds)
		items = self.index.contains(ID, coordinates, True)
		d = self.index.properties.dimension
		return ((map(int,item.bbox[:d]), item.object) for item in items)
 
if __name__ == "__main__":

	d = BinaryDict()
