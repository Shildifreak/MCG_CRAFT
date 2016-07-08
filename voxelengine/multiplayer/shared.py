import sys
if sys.version >= "3":
    raw_input = input

import textures
TEXTURES = [None]
BLOCK_ID_BY_NAME = {"AIR":0}
for name, transparency, top, bottom, side in textures.textures:
    BLOCK_ID_BY_NAME[name] = (len(TEXTURES)<<1)+(not transparency)

# list of possible events, order of bytes to transmit
ACTIONS = ["inv1","inv2","inv3","inv4","inv5","inv6","inv7","inv8",
           "inv9","inv0",
           "for" ,"back","left","right","jump","fly","inv","shift",]

class Vector(tuple):
    def _assert_same_length(self,other):
        if len(self) != len(other):
            raise ValueError("incompatible length adding vectors")
        
    def __add__(self,other):
        self._assert_same_length(other)
        return Vector(map(lambda (s,o):s+o,zip(self,other)))

    def __sub__(self,other):
        self._assert_same_length(other)
        return Vector(map(lambda (s,o):s-o,zip(self,other)))

    def __mul__(self,other):
        if isinstance(other,(float,int)):
            return Vector(map(lambda x: x*other,self))
        else:
            return Vector(map(lambda (s,o):s*o,zip(self,other)))

    def __rshift__(self,other):
        return Vector([i>>other for i in self])

    def __lshift__(self,other):
        return Vector([i<<other for i in self])

    def __mod__(self,other):
        return Vector([i%other for i in self])

    def __radd__(self,other):
        return self+other

    def __rsub__(self,other):
        return Vector(other)-self

    def __rmul__(self,other):
        return self*other

    def normalize(self):
        return Vector(map(int,map(round,self)))

def hit_test(block_at_func, position, direction, max_distance=8):
    """ Line of sight search from current position. If a block is
    intersected it is returned, along with the block previously in the line
    of sight. If no block is found, return None, None.

    Parameters
    ----------
    block_at_func : function used to test wether there is
        a block at a given position
    position : tuple of len 3
        The (x, y, z) position to check visibility from.
    direction : tuple of len 3
        The line of sight vector.
    max_distance : int
        How many blocks away to search for a hit.

    """
    m = 8
    position = Vector(position)
    direction = Vector(direction)
    previous = position.normalize()
    for _ in xrange(max_distance * m):
        key = position.normalize()
        if key != previous and block_at_func(key):
            return key, previous
        previous = key
        position += direction*(1.0/m)
    return None, None

def select(options):
    """
    Return (index, option) the user choose.
    """
    if not options:
        raise ValueError("no options given")
    print "\n".join([" ".join(map(str,option)) for option in enumerate(options)])
    print "Please enter one of the above numbers to select:",
    while True:
        i = raw_input("")
        try:
            return int(i), options[int(i)]
        except ValueError:
            print "Please enter one of the above NUMBERS to select:",
        except IndexError:
            print "Please enter ONE OF THE ABOVE numbers to select:",
