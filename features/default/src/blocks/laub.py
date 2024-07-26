from resources import *

import random


class LAUB(Block):
    defaults = Block.defaults.copy()
    defaults["d_wood"] = 0
    MAXDISTANCE = 10

    def handle_event_block_update(self,event):
        ds = [self.MAXDISTANCE]
        for dpos in FACES:
            block = self.relative[dpos]
            if block == "HOLZ":
                d_wood = 0
                break
            if block["id"] == "LAUB":
                ds.append(block["d_wood"])
        else:
            d_wood = min(ds) + 1
        if self["d_wood"] != d_wood:
            self["d_wood"] = d_wood
            return True
        return False

    def handle_event_random_tick(self, event):
        if self["d_wood"] >= self.MAXDISTANCE:
            self.turn_into("AIR")
            itemid = random.choices(["LAUB","Stick1","Stick2","Stick3","Setzling","Apple"],[6,1,1,1,1,1])[0]
            e = EntityFactory({"type":"Item","item":{"id":itemid}})
            e.set_world(self.world,self.position)
            e.add_random_velocity()
            return True
        return False

    def get_tags(self):
        return super().get_tags() | {"block_update", "random_tick"}
