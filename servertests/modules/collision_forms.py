import collections, math, itertools

import sys
sys.path.append("../../../lib/voxelengine/modules")
from shared import Vector

class Area(object):
	def binary_box_cover():
		"""return a set of binary boxes so that everything that collides with self collides with one of the binary boxes"""
		raise NotImplementedError()
	
	def collides_with(self, other, count_touch_without_intersection = False):
		d = self.distance(other)
		if count_touch_without_intersection:
			return d <= 0
		return d < 0
	
	def distance(self, other):
		"""some number that is negative if the areas collide, 0 if they touch and positive if there's space inbetween"""
		if isinstance(other, BinaryBox):
			return self._distance_to_BinaryBox(other)
		if isinstance(other, Box):
			return self._distance_to_Box(other)
		#if isinstance(other, Point):
		#	return self._distance_to_Point(other)
		if isinstance(other, Sphere):
			return self._distance_to_Sphere(other)
		if isinstance(other, Ray):
			return self._distance_to_Ray(other)

	def _distance_to_BinaryBox(self, other):
		raise NotImplementedError()
	def _distance_to_Box(self, other):
		raise NotImplementedError()
	#def _distance_to_Point(self, other):
	#	self._distance_to_Sphere(other)
	def _distance_to_Sphere(self, other):
		raise NotImplementedError()
	def _distance_to_Ray(self, other):
		raise NotImplementedError()
	

class BinaryBox(collections.namedtuple("BinaryBox",["scale","position"]), Area):
	def bounding_box(self):
		return Box(Vector(self.position)<<self.scale, Vector(p+1 for p in self.position)<<self.scale)

	def get_parent_box(self):
		pass
	def get_child_boxes(self):
		pass
	
	def binary_box_cover(self):
		yield self

	def _distance_to_BinaryBox(self, other):
		"""collision is trivial, touching not"""
		d_scale = other.scale - self.scale
		p_self = self.position >> max(d_scale, 0)
		p_other = other.position >> max(-d_scale, 0)
		if p_self == p_other:
			return -1
		#if not count_touch_without_intersection:
		#	return 1
		direction = sign(p_other - p_self)
		if d_scale > 0:
			p_self = (self.position + direction) >> max(d_scale, 0)
		else:
			p_other = (other.position - direction) >> max(-d_scale, 0)
		if p_self == p_other:
			return 0
		return 1
		
	def _distance_to_Box(self, other):
		raise NotImplementedError()
	def _distance_to_Sphere(self, other):
		raise NotImplementedError()
	def _distance_to_Ray(self, other):
		raise NotImplementedError()

def log2(x):
	"""return smallest n where abs(x) <= 2**n """
	x = math.ceil(abs(x)) - 1
	return 0 if x <= 0 else x.bit_length()

def loground(num):
	return 1 << log2(num)

def floorshift(x, shift):
	x = math.floor(x)
	return (x >> shift)

def ceilshift(x, shift):
	x = math.ceil(x)
	lost = x & ((1 << shift) - 1)
	return (x >> shift) + bool(lost)

def _t(x, n=10):
	"""get a n bit 2s-complement representation of integer x"""
	return "".join("1" if x &(1<<i) else "0" for i in range(n))[::-1]

class Box(Area):
	def __init__(self, lower_bounds, upper_bounds):
		self.lower_bounds = lower_bounds
		self.upper_bounds = upper_bounds
	
	def old_binary_box_cover(self):
		# get size of binary boxes
		size = log2(max(self.upper_bounds-self.lower_bounds))
		# get start and end position of binary boxes
		bb_lower_bounds = Vector(floorshift(x, size) for x in self.lower_bounds)
		bb_upper_bounds = Vector(ceilshift (x, size) for x in self.upper_bounds)
		#assert min(bb_upper_bounds - bb_lower_bounds) > 0 #M# THINK ABOUT BOXES WITH LENGTH 0 ON ONE OR MORE SIDES!!
		for bb_position in itertools.product(*map(range, bb_lower_bounds, bb_upper_bounds)):
			yield BinaryBox(size, bb_position)
	
	@staticmethod
	def _sizes(upper_bound, lower_bound):
		dif = upper_bound ^ lower_bound
		if dif >= 0:
			size_one_block = dif.bit_length()
			mask = ((1 << size_one_block) - 1) >> 1
		else:
			size_one_block = float("inf")
			mask = -1
		ubsize = ( upper_bound & mask).bit_length() #length of remainder without leading 1s determines size of upper block
		lbsize = (~lower_bound & mask).bit_length() #length of remainder without leading 0s determines size of lower block
		size_two_blocks = max(ubsize, lbsize)
		return size_one_block, size_two_blocks
	
	def binary_box_cover(self):
		oldsize = log2(max(self.upper_bounds-self.lower_bounds))
		# get size of binary boxes
		ubs = map(math.ceil, self.upper_bounds)
		lbs = map(math.floor,self.lower_bounds)
		
		sizes_one_block, sizes_two_blocks = zip(*map(self._sizes, ubs, lbs))
		size = max(sizes_two_blocks)
		# the following increases size in order to save on blocks only if it doesn't increase the covered area
		if all(size + 1 == s for s in sizes_one_block):
			size = size + 1
		# the following increases size in order to save on blocks if the blocks are smaller than the box itself
		if size < oldsize and size+1 in sizes_one_block:
			size = size + 1
		# get start and end position of binary boxes
		bb_lower_bounds = Vector(floorshift(x, size) for x in self.lower_bounds)
		bb_upper_bounds = Vector(ceilshift (x, size) for x in self.upper_bounds)
		#assert min(bb_upper_bounds - bb_lower_bounds) > 0 #M# THINK ABOUT BOXES WITH LENGTH 0 ON ONE OR MORE SIDES!!
		for bb_position in itertools.product(*map(range, bb_lower_bounds, bb_upper_bounds)):
			yield BinaryBox(size, bb_position)
	
	def _distance_to_BinaryBox(self, other):
		raise NotImplementedError()
	def _distance_to_Box(self, other):
		return max(map(max,
			other.lower_bounds - self.upper_bounds,
			self.lower_bounds - other.upper_bounds
		))
	def _distance_to_Sphere(box, sphere):
		#get distance to center of sphere in x,y,z
		d = tuple(map(max,
			box.lower_bounds - sphere.center,
			sphere.center - box.upper_bounds))
		if max(d) < 0:
			return max(d) - sphere.radius
		d_plus = Vector(x if x > 0 else 0 for x in d)
		return d_plus.length() - sphere.radius
		
	def _distance_to_Ray(self, other):
		raise NotImplementedError()

class Sphere(Area):
	def __init__(self, center, radius):
		self.center = center
		self.radius = radius
	
	def binary_box_cover(self):
		return Box(Vector(x - self.radius for x in self.center),
				   Vector(x + self.radius for x in self.center)).binary_box_cover()
	
	def _distance_to_BinaryBox(self, other):
		raise NotImplementedError()
	def _distance_to_Box(self, other):
		return other._distance_to_Sphere(self)
	def _distance_to_Sphere(self, other):
		return (self.center - other.center).sqr_length() - (self.radius + other.radius)**2
	def _distance_to_Ray(self, other):
		raise NotImplementedError()

class Point(Sphere):
	def __init__(self, position):
		super(Point, self).__init__(position, 0)

class Ray(Area):
	def _distance_to_BinaryBox(self, other):
		raise NotImplementedError()
	def _distance_to_Box(self, other):
		raise NotImplementedError()
	def _distance_to_Sphere(self, other):
		raise NotImplementedError()
	def _distance_to_Ray(self, other):
		raise NotImplementedError()


if __name__ == "__main__":
	# TEST CASES
	
	assert log2(0.0) == 0
	assert log2(0.5) == 0
	assert log2(1.0) == 0
	assert log2(1.5) == 1
	assert log2(2.0) == 1
	assert log2(2.5) == 2
	assert log2(4.0) == 2
	assert log2(4.5) == 3
	assert log2(8.0) == 3
	
	assert floorshift(-10,2) << 2 == -12
	assert  ceilshift(-10,2) << 2 ==  -8
	assert floorshift( -8,2) << 2 ==  -8
	assert  ceilshift( -8,2) << 2 ==  -8
	assert floorshift( -7,2) << 2 ==  -8
	assert  ceilshift( -7,2) << 2 ==  -4
	assert floorshift( -5,2) << 2 ==  -8
	assert  ceilshift( -5,2) << 2 ==  -4
	assert floorshift( -4,2) << 2 ==  -4
	assert  ceilshift( -4,2) << 2 ==  -4
	assert floorshift( -3,2) << 2 ==  -4
	assert  ceilshift( -3,2) << 2 ==   0
	assert floorshift(  0,2) << 2 ==   0
	assert  ceilshift(  0,2) << 2 ==   0
	assert floorshift(  1,2) << 2 ==   0
	assert  ceilshift(  1,2) << 2 ==   4
	assert floorshift(  3,2) << 2 ==   0
	assert  ceilshift(  3,2) << 2 ==   4
	assert floorshift(  4,2) << 2 ==   4
	assert  ceilshift(  4,2) << 2 ==   4
	assert floorshift(  5,2) << 2 ==   4
	assert  ceilshift(  5,2) << 2 ==   8
	assert floorshift(  7,2) << 2 ==   4
	assert  ceilshift(  7,2) << 2 ==   8
	assert floorshift(  8,2) << 2 ==   8
	assert  ceilshift(  8,2) << 2 ==   8
	assert floorshift(  9,2) << 2 ==   8
	assert  ceilshift(  9,2) << 2 ==  12
	
	
	def sign(num):
		return 1 if (num > 0) else 0 if (num == 0) else -1

	def test(area1, area2, expected_sign):
		d1 = area1.distance(area2)
		d2 = area2.distance(area1)
		assert d1 == d2
		assert expected_sign == sign(d1)

	test(BinaryBox(0, 0),BinaryBox(0, 0),-1)
	test(BinaryBox(1, 0),BinaryBox(1, 0),-1)
	test(BinaryBox(0, 1),BinaryBox(0, 1),-1)
	test(BinaryBox(1, 3),BinaryBox(5, 0),-1)
	test(BinaryBox(0,-1),BinaryBox(0, 0), 0)
	test(BinaryBox(0, 1),BinaryBox(0, 2), 0)
	test(BinaryBox(1, 1),BinaryBox(2, 1), 0)
	test(BinaryBox(2, 0),BinaryBox(1, 2), 0)
	test(BinaryBox(0,-1),BinaryBox(0, 1), 1)
	test(BinaryBox(0, 0),BinaryBox(1, 1), 1)
	test(BinaryBox(0,-1),BinaryBox(1,-2), 1)
	
	test(Box(Vector((0,0,0)), Vector((0,0,0))), Box(Vector((0,0,0)), Vector((0,0,0))), 0)
	print(tuple(Box(Vector((0,0,1)), Vector((1,1,1))).binary_box_cover()))
	# add more box - box tests

	test(Sphere(Vector((0,0,0)), 1), Sphere(Vector((0,0,3)), 2), 0)
	# add more sphere - sphere tests
	
	# add box - sphere tests!
	test(Box(Vector((0,0,0)), Vector((0,0,0))), Sphere(Vector((  0,  0,  0)),   0), 0)
	test(Box(Vector((0,0,1)), Vector((1,1,2))), Sphere(Vector((0.5,0.5,0.5)),   0), 1)
	test(Box(Vector((0,0,1)), Vector((1,1,2))), Sphere(Vector((0.5,0.5,0.5)), 0.5), 0)
	test(Box(Vector((0,0,1)), Vector((1,1,2))), Sphere(Vector((0.5,0.5,0.5)),   1),-1)
	test(Box(Vector((0,0,0)), Vector((1,1,1))), Sphere(Vector((  4,  5,0.5)),   4), 1)
	test(Box(Vector((0,0,0)), Vector((1,1,1))), Sphere(Vector((  4,  5,0.5)),   5), 0)
	test(Box(Vector((0,0,0)), Vector((1,1,1))), Sphere(Vector((  4,  5,0.5)),   6),-1)
	
	print("all tests passed")
