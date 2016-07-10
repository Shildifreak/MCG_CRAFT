#* encoding:utf-8 *#

#Chunkformat: (maybe make somehow sure not to save empty chunks) -> ach was die 26byte machen den Hasen nicht fett
#   bytearray of Chunksize**3 * [blockbytes]
#   blockbytes: blockid containing transparency as last bit, where 0 is transparent and 1 is opaque

#Archiv mit Chunks (Dateiname <[+-]x[+-]y>)
#sollte man dann überhaupt nur sichtbare Blöcke übertragen oder einfach alle?
import zlib
import struct

class Chunk(object):
    # Not threadsave!
    _compressed_data = None     #-either one of these must exist, if both exist they must be konsistent
    _decompressed_data = None   #/
    def __init__(self, data, is_compressed, blockformat="H", chunksize=16):
        """blockformat: format string as specified by struct module
        using blockformat="H" and with 1 bit for transparency 32767 is highest possible block_id"""
        self.blockformat = blockformat
        self.byte_per_block = struct.calcsize(self.blockformat)
        self.chunksize = chunksize
        if is_compressed:
            self._compressed_data = data
        else:
            self._decompressed_data = bytearray(data)
    
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

    def _load_decompressed(self):
        if not self._decompressed_data:
            self._decompressed_data = bytearray(zlib.decompress(self._compressed_data))

    def __setitem__(self,key,value):
        """allow for setting slices so e.g. filling chunk by hightmap becomes easier"""
        s = self.byte_per_block
        vs = struct.pack(self.blockformat,value)
        if isinstance(key,slice):
            start,stop,step = key.indices(len(self._decompressed_data)//s)
            l = len(xrange(start,stop,step))
            start = s*start
            stop  = s*stop
            step  = s*step
            for o,v in enumerate(vs):
                self._decompressed_data[start+o:stop+o:step] = v*l
        else:
            for o,v in enumerate(vs):
                self._decompressed_data[s*key+o] = v
        self._compressed_data = None

    def get_block(self,position):
        """returns tuple!"""
        i = position #M# do some magic here
        self._load_decompressed()
        return struct.unpack_from(self.blockformat,self._decompressed_data,i*self.byte_per_block)

    def set_block(self,position,*values):
        i = position #M# do some magic here
        self._load_decompressed()
        struct.pack_into(self.blockformat,self._decompressed_data,i*self.byte_per_block,*values)
        self._compressed_data = None

    def compress(self):
        """make sure data is saved ONLY in compressed form, thereby saving memory"""
        self.compressed_data #calling property makes sure _compressed_data is set
        self._decompressed_data = None

c = Chunk("\x00"*16**3,False)
c[50:300:] = 300
for i in range(10):
    print c.get_block(i)
print c.compressed_data

help(c)

raw_input("waiting...")

a = bytearray("a"*16**3)
c = zlib.compress(buffer(a))
#with open("testfile","wb") as savestate:
#    savestate.write(c)

import zipfile
with zipfile.ZipFile("ziptest.zip","w"  ,allowZip64=True) as zf:
    for x in range(16**3):
        zf.writestr(str(x),c)