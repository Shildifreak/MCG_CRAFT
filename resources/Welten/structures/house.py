
def house_structure(l,b):

    #Boden
    for x in range(0,b+1):
        for z in range(1,l):
            yield (x,0,z), "HOLZBRETTER"

    h=(l+b)//4
    
    #Wände        
    for y in range(0,h):
        for x in range(0,b+1):
            yield (x,y,0), "HOLZBRETTER"
            yield (x,y,l), "HOLZBRETTER"
        for z in range(0,l):
            yield (0,y,z), "HOLZBRETTER"
            yield (b,y,z), "HOLZBRETTER"
            
    #Rand von Holzstämmen zum dach
    for x in range(0,b+1):
        yield (x,h,0), {"id":"HOLZ","base":"w"}
        yield (x,h,l), {"id":"HOLZ","base":"w"}
    for z in range(0,l):
        yield (0,h,z), {"id":"HOLZ","base":"n"}
        yield (b,h,z), {"id":"HOLZ","base":"n"}
        
    #Holzstämme säulen
    for y in range(0,h+1):
        yield (0,y,0), "HOLZ"
    for y in range(0,h+1):
        yield (b,y,l), "HOLZ"
    for y in range(0,h+1):
        yield (0,y,l), "HOLZ"
    for y in range(0,h+1):
        yield (b,y,0), "HOLZ"
        
    #Dach
    for i in range (0,5):
        for x in range(-1+i,b+(2-i)):
            for z in range(-1+i,l+(2-i)):
                yield (x,h+1+i,z), "BRICK"
            
    #Dachloch 1        
    for i in range (2,6):
        for x in range(i,b-i+1):
            for z in range(i,l-i+1):
                yield (x,h-1+i,z), "AIR"
