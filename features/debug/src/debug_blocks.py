from resources import *

class INITPRINT(Block):
	def __init__(self,*args, **kwargs):
		super().__init__(*args, **kwargs)
		print()
		print("INITPRINT.__init__(",",".join(map(str,args)),kwargs.keys(),")")
