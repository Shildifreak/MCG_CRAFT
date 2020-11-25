l = []
v = 0.8
px = 1/16
for s in range(4):
    for o,x in [("ON",5),("OFF",6)]:
        l.append(["repeater"+str(s)+o,True,(6,5),[[],[],[],[],[],[],[(0,0.1,0, 1,0.1,0, 1,0.1,1, 0,0.1,1),(
