
def house_structure(l,b):
    for x in range(0,b-1):
        for y in range(1,l-1):
            yield (x,0,y), "HOLZBRETTER"
    for i in range(1,6):
        for x in range(-1,b-1):
            yield (x,i,0), "HOLZBRETTER"
            yield (x,i,l), "HOLZBRETTER"
        for y in range(0,l):
            yield (0,i,y), "HOLZBRETTER"
            yield (b-1,i,y), "HOLZBRETTER"
    
    for x in range(-1,b-1,b):
        for y in range(0,l,l):
            for h in range(1,5):
                yield (x,h,y), "HOLZ"
    
