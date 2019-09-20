
import bisect
import itertools

class BinaryDict(object):
	
	def __init__(self,data=()):
		#data contains dummy element so that bisect always gives a valid index
		self.data = [((float("inf"),),None,None)] # [(zipped_ints, position, content),..] sorted by zipped_xyz
		
		for key, value in data:
			self[key] = value
	
	def __getitem__(self, position):
		key = binary_zip(*position)
		i = bisect.bisect_right(self.data, (key,))
		k, p, v = self.data[i]
		if k == key:
			return v
		else:
			raise KeyError(position)
	
	def __setitem__(self, position, value):
		key = binary_zip(*position)
		i = bisect.bisect_right(self.data, (key,))
		if self.data[i][0] == key:
			self.data[i] = (key, position, value)
		else:
			self.data.insert(i, (key, position, value))
	
	def __delitem__(self, position):
		self.pop(position)
		
	def pop(self, position):
		key = binary_zip(*position)
		i = bisect.bisect_right(self.data, (key,))
		if self.data[i][0] == key:
			return self.data.pop(i)
		else:
			raise KeyError(position)
	
	def __repr__(self):
		return repr(self.data)
	
	def __len__(self):
		return len(self.data) - 1

	def list_blocks_in_binary_box(self, binary_box):
		"""return all blocks that are in binary_box"""
		one = (1,)*len(binary_box.position)
		low_pos = binary_box.position << binary_box.scale
		high_pos = (binary_box.position + one << binary_box.scale) - one
		low_pos2 = (min(i,key=abs) for i in zip(low_pos, high_pos))
		high_pos2 = (max(i,key=abs) for i in zip(low_pos, high_pos))
		low_key = binary_zip(*low_pos2)
		high_key = binary_zip(*high_pos2)
		low_i = bisect.bisect_right(self.data, (low_key,))
		high_i = bisect.bisect_right(self.data, (high_key,))
		return ((position, value) for _,position,value in self.data[low_i:high_i])

def binary_zip2(*ints):
	signs = int("".join(str(int(i<0)) for i in ints),2)
	ints = tuple(i if i>=0 else i^-1 for i in ints)
	length = max(i.bit_length() for i in ints)
	ints_bin = tuple(bin(i)[2:].zfill(length) for i in ints)
	ints_bin_zipped = itertools.chain.from_iterable(zip(*ints_bin))
	ints_zipped = int("".join(ints_bin_zipped),2)
	return (signs, ints_zipped)

def binary_zip(x,y,z):
	xs, ys, zs = x<0, y<0, z<0
	signs = (xs<<2) + (ys<<1) + zs
	x ^= -xs
	y ^= -ys
	z ^= -zs
	bx = bin(x)[:1:-1]
	by = bin(y)[:1:-1]
	bz = bin(z)[:1:-1]
	bs = "".join(itertools.chain.from_iterable(itertools.zip_longest(bz,by,bx,fillvalue="0")))[::-1]
	ints_zipped = int(bs,2)
	return signs, ints_zipped

def binary_zip3(*ints):
	ints = ints[::-1]
	int_s = tuple(i<0 for i in ints)
	signs = sum(s<<n for n,s in enumerate(int_s))
	ints_bin = tuple(bin(i^-s)[:1:-1] for i,s in zip(ints, int_s))
	bs = "".join(itertools.chain.from_iterable(itertools.zip_longest(*ints_bin,fillvalue="0")))[::-1]
	ints_zipped = int(bs,2)
	return signs, ints_zipped

if __name__ == "__main__":
	
	print(binary_zip(1,2,3))
	print(binary_zip(-2,2,-4))
	print(binary_zip(-1,2,-3))


	d = BinaryDict()
	d[1,2,3] = "a"
	print(d)
	d[1,2,3] = "b"
	print(d)
	d[1,2,4] = "c"
	print(d)
	d[0,0,-3] = "0,0,-3"
	d[0,0,-2] = "0,0,-2"
	d[0,0,-1] = "0,0,-1"
	d[0,0,0] = "0,0,0"
	d[0,0,1] = "0,0,1"
	d[0,0,2] = "0,0,2"
	d[0,0,3] = "0,0,3"
	d[0,0,4] = "0,0,4"
	d[0,0,5] = "0,0,5"
	#d[0,1,0] = "0,1,0"
	#d[0,1,1] = "0,1,1"
	#d[1,0,0] = "1,0,0"
	#d[1,0,1] = "1,0,1"
	#d[1,1,0] = "1,1,0"
	#d[1,1,1] = "1,1,1"
	print(d)
	
	import timeit, random
	n = 100000
	samples = [random.sample(range(-100,100),3) for _ in range(n)]
	def wrapper(f, iterator):
		def f_new():
			return f(*next(iterator))
		return f_new
	
	print( timeit.timeit(wrapper(binary_zip, iter(samples)), number=n) )
	print( timeit.timeit(wrapper(binary_zip2,iter(samples)), number=n) )
	print( timeit.timeit(wrapper(binary_zip3,iter(samples)), number=n) )
	
	
	for sample in samples[:10]:
		print(binary_zip(*sample),
			  binary_zip2(*sample),
			  binary_zip2(*sample),
			 )

	if False:
		from collections import namedtuple
		from shared import Vector
		BinaryBox = namedtuple("BinaryBox",["scale","position"])
		print(tuple(d.list_blocks_in_binary_box(BinaryBox(1,Vector(0,0,-1)))))
