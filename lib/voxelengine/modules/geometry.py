import sys, os
if __name__ == "__main__":
    sys.path.append(os.path.abspath("../.."))
    __package__ = "voxelengine.modules"

import collections, math, itertools, operator

from voxelengine.modules.utils import floatrange

class Vector(tuple):
    __slots__ = ()
    def __new__(cls, *args):
        if len(args) == 1:
            return super().__new__(cls, args[0])
        else:
            return super().__new__(cls, args)
    
    def _assert_same_length(self,other):
        if len(self) != len(other):
            raise ValueError("incompatible length adding vectors")
        
    def __add__(self,other):
        self._assert_same_length(other)
        #return Vector(s+o for s,o in zip(self, other))
        return Vector(map(operator.add, self, other))

    def __sub__(self,other):
        self._assert_same_length(other)
        #return Vector(s-o for s,o in zip(self, other))
        return Vector(map(operator.sub, self, other))        

    def __mul__(self,other):
        if isinstance(other,(float,int)):
            return Vector(i*other for i in self)
        else:
            #return Vector(s*o for s,o in zip(self, other))
            return Vector(map(operator.mul, self, other))

    def __truediv__(self,other):
        if isinstance(other,(float,int)):
            return Vector(i/other for i in self)
        else:
            return Vector(map(operator.div, self, other))

    def __rshift__(self,other):
        return Vector(i>>other for i in self)

    def __lshift__(self,other):
        return Vector(i<<other for i in self)

    def __mod__(self,other):
        return Vector(i%other for i in self)

    def __neg__(self):
        return Vector(-e for e in self)
        
    def __xor__(self, other):
        if isinstance(other, int):
            return Vector(i^other for i in self)
        else:
            return Vector(map(operator.xor, self, other))


    def __radd__(self,other):
        return self+other

    def __rsub__(self,other):
        return Vector(other)-self

    def __rmul__(self,other):
        return self*other
    
    def __rdiv__(self,other):
        raise NotImplementedError()
    
    def __rxor__(self,other):
        return self^other

    def add_scalar(self, other):
        return Vector(i+other for i in self)

    def round(self):
        return Vector(int(round(i)) for i in self)

    def length(self):
        return self.sqr_length()**0.5
    
    def sqr_length(self):
        #return sum(map(operator.mul,self,self))
        return sum(i**2 for i in self)

    def normalize(self):
        return self / self.length()

    def __str__(self):
        return " ".join(map(str,self))
    
    def __repr__(self):
        return "Vector"+tuple.__repr__(self)

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
        if isinstance(other, Box):
            return self._distance_to_Box(other)
        #if isinstance(other, Point):
        #   return self._distance_to_Point(other)
        if isinstance(other, Sphere):
            return self._distance_to_Sphere(other)
        if isinstance(other, Ray):
            return self._distance_to_Ray(other)
        if isinstance(other, Everywhere):
            return -1
        if isinstance(other, Nowhere):
            return 1
        raise ValueError("Can't calculate distance to object of type %s" % type(other))

    def _distance_to_Box(self, other):
        raise NotImplementedError()
    #def _distance_to_Point(self, other):
    #   self._distance_to_Sphere(other)
    def _distance_to_Sphere(self, other):
        raise NotImplementedError()
    def _distance_to_Ray(self, other):
        raise NotImplementedError()
    
    def __contains__(self, position):
        return self._distance_to_Sphere(Point(Vector(position))) <= 0

class BinaryBox(collections.namedtuple("BinaryBox",["scale","position"])):
    def bounding_box(self):
        anchor_point = Vector(self.position)<<self.scale
        lower_bounds = anchor_point.add_scalar(-0.5) # offset because blocks have their anchorpoint in the center
        upper_bounds = lower_bounds.add_scalar(1<<self.scale)
        return Box(lower_bounds, upper_bounds)

    def get_parent(self):
        return BinaryBox(self.scale+1, Vector(self.position)>>1)

    def get_children(self):
        for offset in itertools.product((0,1),repeat=len(self.position)):
            yield BinaryBox(self.scale-1, (Vector(self.position)<<1)+offset)

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
        self.lower_bounds = Vector(lower_bounds)
        self.upper_bounds = Vector(upper_bounds)

    def __add__(self, offset):
        return Box(self.lower_bounds+offset, self.upper_bounds+offset)

    def __radd__(self, other):
        return self + other

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
        ubs = self.upper_bounds.round()
        lbs = self.lower_bounds.round()
        
        sizes_one_block, sizes_two_blocks = zip(*map(self._sizes, ubs, lbs))
        size = max(sizes_two_blocks)
        # the following increases size in order to save on blocks only if it doesn't increase the covered area
        if all(size + 1 == s for s in sizes_one_block):
            size = size + 1
        # the following increases size in order to save on blocks if the blocks are smaller than the box itself
        if size < oldsize and size+1 in sizes_one_block:
            size = size + 1
        # get start and end position of binary boxes
        bb_lower_bounds = lbs >> size
        bb_upper_bounds = ubs >> size
        for bb_position in itertools.product(*map(range, bb_lower_bounds, bb_upper_bounds.add_scalar(1))):
            yield BinaryBox(size, Vector(bb_position))
    
    def _distance_to_BinaryBox(self, other):
        return self._distance_to_Box(other)
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
    
    def __repr__(self):
        return "Box" + repr((self.lower_bounds, self.upper_bounds)) # Box(lower_bounds, upper_bounds)
        
    def __str__(self):
        return " ".join(map(str, (*self.lower_bounds, *self.upper_bounds)))

class Sphere(Area):
    def __init__(self, center, radius):
        self.center = center
        self.radius = radius
    
    def __add__(self, offset):
        return Sphere(self.center+offset, self.radius)

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

    def __repr__(self):
        return "Sphere" + repr((self.center, self.radius)) #Sphere(center, radius)

class Ray(Area):
    __slots__ = ("origin", "direction", "dirfrac")
    def __init__(self, origin, direction):
        self.origin = origin
        self.direction = direction
        self.dirfrac = Vector((1.0/d if d!=0 else float("inf")) for d in direction)

    def bounding_box(self, length):
        c1 = self.origin
        c2 = self.origin+self.direction.normalize()*length
        lower_bounds = map(min,c1,c2)
        upper_bounds = map(max,c1,c2)
        return Box(lower_bounds, upper_bounds)

    def distance_from_origin_to_Box(self, box):
        """returns False if no collision else distance from origin of ray to front of box,
        this can be negative if origin is inside box"""
        # based on https://gamedev.stackexchange.com/questions/18436/most-efficient-aabb-vs-ray-collision-algorithms
        t135 = (box.lower_bounds - self.origin)*self.dirfrac
        t246 = (box.upper_bounds - self.origin)*self.dirfrac

        tmin = max(map(min,t135,t246))
        tmax = min(map(max,t135,t246))

        # if tmax < 0, ray (line) is intersecting AABB, but the whole AABB is behind us
        # if tmin > tmax, ray doesn't intersect AABB
        if (tmax < 0) or (tmin > tmax):
            return False
        return tmin

    def __add__(self, offset):
        raise NotImplementedError()
    def _distance_to_BinaryBox(self, other):
        raise NotImplementedError()
    def _distance_to_Box(self, box):
        """this method has to return negative distance when intersecting,
        so it wraps the more intuitive distance_from_origin_to_Box function"""
        d = self.distance_from_origin_to_Box(box)
        if d == False:
            return 1
        else: # d can still be positive or negative depending on whether origin of ray is in front of Box or inside
            return -1
    def _distance_to_Sphere(self, other):
        raise NotImplementedError()
    def _distance_to_Ray(self, other):
        raise NotImplementedError()

    def hit_test(self, block_at_func, max_distance):
        """ Line of sight search from current position.
        returns (distance, blockpos, face)
        If no block is found, return (None, None, None).

        Parameters
        ----------
        block_at_func : function used to test wether there is
            a block at a given position
        max_distance : float
            How many blocks away to search for a hit.

        """
        position = self.origin
        block_pos = position.round()
        offset = Vector(0.5 if d >= 0 else -0.5 for d in self.direction)
        distance = 0
        dx,dy,dz = self.direction
        dpx = Vector(((1 if dx >= 0 else -1), 0, 0))
        dpy = Vector((0, (1 if dy >= 0 else -1), 0))
        dpz = Vector((0, 0, (1 if dz >= 0 else -1)))    
        l = self.direction.length()
        while True:
            tx,ty,tz = (block_pos+offset-position)
            kx = tx*self.dirfrac[0]
            ky = ty*self.dirfrac[1]
            kz = tz*self.dirfrac[2]
            dp, k = min((dpx,kx),(dpy,ky),(dpz,kz),key=lambda t:t[1])
            distance += l*k
            if k < 0:
                raise RuntimeError("This should not happen and would cause an infinite loop.")
            if distance > max_distance:
                break
            block_pos += dp
            position += k*self.direction
            if block_at_func(block_pos):
                return distance, block_pos, -dp
        return None, None, None

class Everywhere(Area):
    __slots__ = ()
    def distance(self, other):
        return -1
EVERYWHERE = Everywhere()

class Nowhere(Area):
    __slots__ = ()
    def distance(self, other):
        return 1
    def __bool__(self):
        raise NotImplementedError()
NOWHERE = Nowhere()

class Point(Sphere):
    def __init__(self, position):
        super(Point, self).__init__(position, 0)


class Hitbox(Box):
    def __init__(self, width, height, eye_level):
        super(Hitbox, self).__init__(Vector(-width,       -eye_level, -width),
                                     Vector( width, height-eye_level,  width))
        self.hitpoints = [Vector((dx,dy,dz)) for dx in floatrange(-width,width)
                                             for dy in floatrange(-eye_level,height-eye_level)
                                             for dz in floatrange(-width,width)]


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

    test(BinaryBox(0,( 0,)).bounding_box(),BinaryBox(0,( 0,)).bounding_box(),-1)
    test(BinaryBox(1,( 0,)).bounding_box(),BinaryBox(1,( 0,)).bounding_box(),-1)
    test(BinaryBox(0,( 1,)).bounding_box(),BinaryBox(0,( 1,)).bounding_box(),-1)
    test(BinaryBox(1,( 3,)).bounding_box(),BinaryBox(5,( 0,)).bounding_box(),-1)
    test(BinaryBox(0,(-1,)).bounding_box(),BinaryBox(0,( 0,)).bounding_box(), 0)
    test(BinaryBox(0,( 1,)).bounding_box(),BinaryBox(0,( 2,)).bounding_box(), 0)
    test(BinaryBox(1,( 1,)).bounding_box(),BinaryBox(2,( 1,)).bounding_box(), 0)
    test(BinaryBox(2,( 0,)).bounding_box(),BinaryBox(1,( 2,)).bounding_box(), 0)
    test(BinaryBox(0,(-1,)).bounding_box(),BinaryBox(0,( 1,)).bounding_box(), 1)
    test(BinaryBox(0,( 0,)).bounding_box(),BinaryBox(1,( 1,)).bounding_box(), 1)
    test(BinaryBox(0,(-1,)).bounding_box(),BinaryBox(1,(-2,)).bounding_box(), 1)
    
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

    assert Vector(0,0,0) in Box(Vector(-1,-1,-1), Vector(1,1,1))
    
    print("all tests passed")
