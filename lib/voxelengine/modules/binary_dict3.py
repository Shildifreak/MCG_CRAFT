import sys, os
if __name__ == "__main__":
    sys.path.append(os.path.abspath("../.."))
    __package__ = "voxelengine.modules"

import bisect
import itertools

class BinaryNode(list):
    __slots__ = ()
    def __init__(self, zzz = None):
        return list.__init__(self, (zzz,)+(None,)*7)
    
    def getdefault(self, key):
        if self[key] == None:
            self[key] = BinaryNode()
        return self[key]
    
    def __repr__(self):
        return repr({i:x for i,x in enumerate(self) if x})

    def flatten(self, position_prefix, remaining_depth):
        for i, x in enumerate(self):
            position = (position_prefix << 1) + ((i&4)>>2, (i&2)>>1, (i&1))
            if x:
                if remaining_depth == 1:
                    yield (position, x)
                else:
                    yield from x.flatten(position, remaining_depth-1)

class Tree(object):
    def __init__(self, root, height):
        self.root = root
        self.height = height

    def grow(self, d_height):
        print("growing", d_height, self.height)
        for _ in range(d_height):
            self.root = BinaryNode(self.root)
        self.height += d_height

    def __getitem__(self, path, level=0):
        d = self.height - (len(path) + level)
        if d < 0:
            raise KeyError("ähm")
        if d > 0:
            path = (0,)*d + path
        node = self.root
        for tribit in path:
            node = node[tribit]
            if node == None:
                raise KeyError("öhm")
        return node

    def __setitem__(self, path, value):
        d = self.height - len(path)
        if d < 0:
            self.grow(-d)
        if d > 0:
            path = (0,)*d + path
        *path, final_key = path
        node = self.root
        for tribit in path:
            node = node.getdefault(tribit)
        node[final_key] = value

    def pop(self, path):
        raise NotImplementedError()
    
    def __repr__(self):
        return repr(self.root)

class BinaryDict(object):
    
    def __init__(self,data=()):
        if data:
            raise NotImplementedError()
        self.trees = tuple(Tree(BinaryNode(), 1) for _ in range(8))

    def __getitem__(self, position):
        signs, ints_zipped = binary_zip(*position)
        tree = self.trees[signs]
        return tree[ints_zipped]
    
    def __setitem__(self, position, value):
        signs, ints_zipped = binary_zip(*position)
        tree = self.trees[signs]
        tree[ints_zipped] = value
    
    def setdefault(self, position, default):
        signs, ints_zipped = binary_zip(*position)
        tree = self.trees[signs]
        try:
            return tree[ints_zipped]
        except KeyError:
            tree[ints_zipped] = default
            return default
        
    def pop(self, position):
        signs, ints_zipped = binary_zip(*position)
        tree = self.trees[signs]
        tree.pop(ints_zipped)
    
    def __repr__(self):
        return repr(self.trees)
    
    def __len__(self):
        print(Warning("BinaryDict.__len__ is not actually implemented"))
        return 0

    def list_blocks_in_binary_box(self, binary_box):
        signs, ints_zipped = binary_zip(*binary_box.position)
        tree = self.trees[signs]
        scale = binary_box.scale
        if scale == 0:
            return ((binary_box.position, tree[ints_zipped]),)
        if binary_box.scale > tree.height and len(ints_zipped) == 0:
            node = tree.root
            scale = tree.height
        else:
            try:
                node = tree.__getitem__(ints_zipped, scale)
            except KeyError as e:
                return ()
        nsigns = (-((signs&4)>>2), -((signs&2)>>1), -(signs&1))
        return ((position^nsigns, value) for position, value in node.flatten(binary_box.position^nsigns, scale))

def binary_zip(x,y,z):
    xs, ys, zs = x<0, y<0, z<0
    signs = (xs<<2) | (ys<<1) | zs
    x ^= -xs
    y ^= -ys
    z ^= -zs
    bx = bin(x)[:1:-1]
    by = bin(y)[:1:-1]
    bz = bin(z)[:1:-1]
    #ints_zipped = "".join(itertools.chain.from_iterable(itertools.zip_longest(bz,by,bx,fillvalue="0")))[::-1]
    ints_zipped = tuple(int(x+y+z,2) for x,y,z in itertools.zip_longest(bx,by,bz,fillvalue="0"))[::-1]
    if ints_zipped == (0,):
        return signs, ()
    return signs, ints_zipped

def binary_zip2(x,y,z):
    xs, ys, zs = x<0, y<0, z<0
    signs = (xs<<2) | (ys<<1) | zs
    x ^= -xs
    y ^= -ys
    z ^= -zs
    l = (x|y|z).bit_length()
    x <<= 2
    y <<= 1
    ints_zipped = tuple( (x>>i)&4 | (y>>i)&2 | (z>>i)&1 for i in range(l-1,-1,-1))
    return signs, ints_zipped

if __name__ == "__main__":
    print(binary_zip(0,0,0))
    print(binary_zip(-1,-1,0))
    print(binary_zip(1,2,3))
    print(binary_zip(-2,2,-4))
    print(binary_zip(-1,2,-3))

    print(binary_zip2(1,2,3))
    print(binary_zip2(-2,2,-4))
    print(binary_zip2(-1,2,-3))

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
    d[0,1,0] = "0,1,0"
    d[0,1,1] = "0,1,1"
    d[1,0,0] = "1,0,0"
    d[1,0,1] = "1,0,1"
    d[1,1,0] = "1,1,0"
    d[1,1,1] = "1,1,1"
    print(d)
    import pprint
    pprint.pprint(d.trees)

    import timeit, random
    n = 100000
    samples = [random.sample(range(-100,100),3) for _ in range(n)]
    def wrapper(f, iterator):
        def f_new():
            return f(*next(iterator))
        return f_new
    
    print( timeit.timeit(wrapper(binary_zip, iter(samples)), number=n) )
    print( timeit.timeit(wrapper(binary_zip2, iter(samples)), number=n) )

    if True:
        from shared import Vector
        from collections import namedtuple
        BinaryBox = namedtuple("BinaryBox",["scale","position"])
    
        print(tuple(d.list_blocks_in_binary_box(BinaryBox(2,Vector(0,0,-1)))))

