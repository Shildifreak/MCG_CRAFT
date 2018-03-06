from base import *
import random 
@register_block("TNT")

class tntblock(Block):
    blast_resistance =  0
    def block_update(self,faces):
        self.activated(None,None)

    def activated(self,character,face):
        tntrange = 5
        for dx in range(-tntrange,tntrange+1):
            for dy in range(-tntrange,tntrange+1):
                for dz in range(-tntrange,tntrange+1):
                    tp = self.position+(dx,dy,dz)
                    dp = type(self.position)((dx,dy,dz))
                    self.world.get_block_object(tp).exploded(dp.length()/tntrange)
                    
                    
