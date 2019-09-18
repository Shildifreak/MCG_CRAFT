
import bisect
import itertools

class BinaryNode(object):
	__slots__ = "_0", "_1"
	def __init__(self, zero = None, one = None):
		self._0 = zero
		self._1 = one
	
	def get(self, key, grow = False):
		if key == "0":
			if grow and self._0 == None:
				self._0 = BinaryNode()
			return self._0
		else:
			assert key == "1"
			if grow and self._1 == None:
				self._1 = BinaryNode()
			result = self._1
	
	def set(self, key, value):
		if key == "0":
			self._0 = value
		else:
			assert key == "1"
			self._1 = value
	
	def __repr__(self):
		return "Node(%s,%s)" % (repr(self._0), repr(self._1))

class Tree(object):
	def __init__(self, root=None, height=0):
		self.root = root
		self.height = height

	def grow(self, height):
		if self.height > height:
			return
		for _ in range(height - self.height):
			self.root = BinaryNode(self.root)
		self.height = height
	
	def __repr__(self):
		return repr(self.root)

class BinaryDict(object):
	
	def __init__(self,data=()):
		if data:
			raise NotImplementedError()
		self.trees = tuple(Tree(BinaryNode(), 1) for _ in range(8))
	
	def prepare(self, position):
		signs, ints_zipped = binary_zip(*position)
		tree = self.trees[signs]
		if tree.height < len(ints_zipped):
			tree.grow(len(ints_zipped))
		if tree.height > len(ints_zipped):
			ints_zipped = (0,)*(tree.height-len(ints_zipped)) + ints_zipped
		node = tree.root
		return node, ints_zipped

	def __getitem__(self, position):
		node, ints_zipped = self.prepare(position)
		for key in ints_zipped:
			node = node.get(key)
		return node
	
	def __setitem__(self, position, value):
		node, ints_zipped = self.prepare(position)
		for key in ints_zipped[:-1]:
			print(node)
			node = node.get(key, grow=True)
			print(node)
		node.set(ints_zipped[-1], value)
	
	def __delitem__(self, position):
		pass
		
	def pop(self, position):
		pass
	
	def __repr__(self):
		return repr(self.trees)
	
	def __len__(self):
		pass

	def list_blocks_in_binary_box(self, binary_box):
		pass




def binary_zip(x,y,z):
	xs, ys, zs = x<0, y<0, z<0
	signs = (xs<<2) + (ys<<1) + zs
	x ^= -xs
	y ^= -ys
	z ^= -zs
	bx = bin(x)[:1:-1]
	by = bin(y)[:1:-1]
	bz = bin(z)[:1:-1]
	ints_zipped = tuple(itertools.chain.from_iterable(itertools.zip_longest(bz,by,bx,fillvalue="0")))[::-1]
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
	
	if False:
		from shared import Vector
		BinaryBox = namedtuple("BinaryBox",["scale","position"])
	
		print(tuple(d.list_blocks_in_binary_box(BinaryBox(1,Vector(0,0,-1)))))

