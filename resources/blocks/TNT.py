from resources import *
import random

@register_block("TNT")
class tntblock(Block):
    blast_resistance =  0
    def handle_event_block_update(self,event):
        print(event)
        for face in FACES:
            nachbarblockposition = self.position + face
            nachbarblock = self.world[nachbarblockposition]
            if nachbarblock["p_level"] > 0:
                self.activated(None,None)
                break

    def activated(self,character,face):
        tntrange = random.randint(3,7)
        self.world[self.position] = "AIR"
        for dx in range(-tntrange,tntrange+1):
            for dy in range(-tntrange,tntrange+1):
                for dz in range(-tntrange,tntrange+1):
                    tp = self.position+(dx,dy,dz)
                    dp = type(self.position)((dx,dy,dz))
                    self.world[tp].exploded(dp.length()/tntrange)
        
    def handle_event_explosion(self,event):
        if entf < 1:
            self.activated(None,None)

    def get_tags(self):
        return super(tntblock,self).get_tags().union({"block_update"})

@register_block("A-TNT")
class a_tntblock(Block):
    blast_resistance= 0
    def handle_event_block_update(self,event):
        for face in faces:
            nachbarblockposition = self.position + face
            nachbarblock = self.world[nachbarblockposition]
            if nachbarblock["p_level"] > 0:
                self.activated(None,None)
                break

    def activated(self,character,face):
        tntrange = random.randint(14,16)
        self.world[self.position] = "AIR"
        for dx in range(-tntrange,tntrange+1):
            for dy in range(-tntrange,tntrange+1):
                for dz in range(-tntrange,tntrange+1):
                    tp = self.position+(dx,dy,dz)
                    dp = type(self.position)((dx,dy,dz))
                    self.world[tp].exploded(dp.length()/tntrange)
        
    def handle_event_explosion(self,event):
        if entf < 1:
            self.activated(None,None)

    def get_tags(self):
        return super(a_tntblock,self).get_tags().union({"block_update"})

@register_block("B-TNT")
class b_tntblock(Block):
    blast_resistance= 0
    def handle_event_block_update(self,event):
        for face in faces:
            nachbarblockposition = self.position + face
            nachbarblock = self.world[nachbarblockposition]
            if nachbarblock["p_level"] > 0:
                self.activated(None,None)
                break

    def activated(self,character,face):
        tntrange = random.randint(14,16)
        self.world[self.position] = "AIR"
        dy = -1
        for dx in range(-tntrange,tntrange+1):
            for dz in range(-tntrange,tntrange+1):
                tp = self.position+(dx,dy,dz)
                dp = type(self.position)((dx,dy,dz))
                self.world[tp].exploded(dp.length()/tntrange)
        
    def handle_event_explosion(self,event):
        if entf < 1:
            self.activated(None,None)

    def get_tags(self):
        return super(b_tntblock,self).get_tags().union({"block_update"})
