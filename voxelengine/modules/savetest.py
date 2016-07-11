#* encoding:utf-8 *#

#Archiv mit Chunks (Dateiname <[+-]x[+-]y>)
import zlib
import zipfile

#raw_input("waiting...")

a = bytearray("a"*16**3)
c = zlib.compress(buffer(a))
#with open("testfile","wb") as savestate:
#    savestate.write(c)

with zipfile.ZipFile("ziptest.zip","w"  ,allowZip64=True) as zf:
    zf.writestr("c_1_1","hello")
    zf.writestr("c_1_2","bye")
    zf.writestr("entities","joram")

with zipfile.ZipFile("ziptest.zip","r"  ,allowZip64=True) as zf:
    for name in zf.namelist():
        print zf.read(name)
    zf.read("noname")