import sys
if sys.version >= "3":
    raw_input = input

import struct
import zlib

# maybe in own config.py?
CHUNKSIZE = 3 # (in bit -> length is 2**CHUNKSIZE)
DIMENSION = 3
TEXTURE_SIDE_LENGTH = 16
DEFAULT_FOCUS_DISTANCE = 8

import textures
BLOCK_ID_BY_NAME = {"AIR":0}
BLOCK_NAME_BY_ID = ["AIR"]
TRANSPARENCY = [True] #this first value is for air
SOLIDITY = [False] #this as well #M# maybe make air a normal block in the textures.py
for i, (name, transparency, solidity, top, bottom, side) in enumerate(textures.textures):
    BLOCK_ID_BY_NAME[name] = i+1
    BLOCK_NAME_BY_ID.append(name)
    TRANSPARENCY.append(transparency)
    SOLIDITY.append(solidity)

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
    of sight. If no block is found, return (None, None).

    Parameters
    ----------
    block_at_func : function used to test wether there is
        a block at a given position
    position : tuple of len 3
        The (x, y, z) position to check visibility from.
    direction : tuple of len 3
        The line of sight vector.
    max_distance : float
        How many blocks away to search for a hit.

    """
    m = 8
    position = Vector(position)
    direction = Vector(direction)
    previous = position.normalize()
    for _ in xrange(int(max_distance * m)):
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

class Chunk(object):
    """
    Not threadsave!
    #_compressed_data   -either one of these must exist when using chunk, if both exist they must be konsistent
    #_decompressed_data /
    blockformat: format string as specified by struct module
    using blockformat="H" and with 1 bit for transparency 32767 is highest possible block_id
    """
    blockformat = "H"
    byte_per_block = struct.calcsize(blockformat) #make sure to change this if you change the blockformat at runtime
    altered = False #M# not tracked yet

    def init_data(self):
        """fill chunk with zeros"""
        c = (1<<CHUNKSIZE)**3*self.byte_per_block
        self.decompressed_data = bytearray(c)
        self._compressed_data = None
    
    @property
    def compressed_data(self):
        """Compressed version of the blocks in the chunk. Use this for load/store and sending to client."""
        if not self._compressed_data:
            self._compressed_data = zlib.compress(buffer(self._decompressed_data))
        return self._compressed_data
    @compressed_data.setter
    def compressed_data(self,data):
        self._compressed_data = data
        self._decompressed_data = None    
        self.altered = True

    @property
    def decompressed_data(self):
        self._load_decompressed()
        return buffer(self._decompressed_data)
    @decompressed_data.setter
    def decompressed_data(self,data):
        self._decompressed_data = bytearray(data)
        self._compressed_data = None
        self.altered = True

    def _load_decompressed(self):
        if not self._decompressed_data:
            try:
                self._decompressed_data = bytearray(zlib.decompress(self._compressed_data))
            except:
                print self._compressed_data
                raise

    def __setitem__(self,key,value):
        """allow for setting slices so e.g. filling chunk by hightmap becomes easier"""
        self._load_decompressed()
        if isinstance(key,slice):
            s = self.byte_per_block
            vs = struct.pack(self.blockformat,value)
            start,stop,step = key.indices(len(self._decompressed_data)//s)
            l = len(xrange(start,stop,step))
            start = s*start
            stop  = s*stop
            step  = s*step
            for o,v in enumerate(vs):
                self._decompressed_data[start+o:stop+o:step] = v*l
        else:
            struct.pack_into(self.blockformat,self._decompressed_data,key*self.byte_per_block,value)
        self._compressed_data = None
        self.altered = True

    def __getitem__(self,index):
        self._load_decompressed()
        return struct.unpack_from(self.blockformat,self._decompressed_data,index*self.byte_per_block)[0]

    def get_block(self,position):
        return self[self.pos_to_i(position)]

    def set_block(self,position,value):
        self[self.pos_to_i(position)] = value

    def pos_to_i(self, position):
        # reorder to y-first for better compression
        position = position%(1<<CHUNKSIZE)
        i = reduce(lambda x,y:(x<<CHUNKSIZE)+y,position)
        return i

    def compress(self):
        """make sure data is saved ONLY in compressed form, thereby saving memory"""
        self.compressed_data #calling property makes sure _compressed_data is set
        self._decompressed_data = None
