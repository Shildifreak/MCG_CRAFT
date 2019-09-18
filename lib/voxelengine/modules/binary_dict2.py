
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

    def grow(self, d_height):
        for _ in range(d_height):
            self.root = BinaryNode(self.root)
        self.height += d_height

    def __getitem__(self, path, level=0):
        """path: list of ones and zeros starting with a one"""
        assert path[0] == "1"
        d = self.height - len(path)
        if d < 0:
            raise KeyError()
        node = self.root
        for _ in range(d - level):
            node = node._0
        for bit in path:
            if node == None:
                raise KeyError()
            node = node._0 if bit == "0" else node._1
        return node

    def __setitem__(self, path, value):
        assert path[0] == "1"
        d = self.height - len(path)
        if d < 0:
            self.grow(-d)

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
        
    def pop(self, position):
        signs, ints_zipped = binary_zip(*position)
        tree = self.trees[signs]
        tree.pop(ints_zipped)
    
    def __repr__(self):
        return repr(self.trees)
    
    def __len__(self):
        raise NotImplementedError()

    def list_blocks_in_binary_box(self, binary_box):
        raise NotImplementedError()




def binary_zip(x,y,z):
    xs, ys, zs = x<0, y<0, z<0
    signs = (xs<<2) + (ys<<1) + zs
    x ^= -xs
    y ^= -ys
    z ^= -zs
    bx = bin(x)[:1:-1]
    by = bin(y)[:1:-1]
    bz = bin(z)[:1:-1]
    ints_zipped = "".join(itertools.chain.from_iterable(itertools.zip_longest(bz,by,bx,fillvalue="0")))[::-1]
    return signs, ints_zipped.lstrip("0")

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

