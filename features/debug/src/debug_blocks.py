from resources import *

@register_block("INITPRINT")
class InitPrintBlock(Block):
	def __init__(self,*args, **kwargs):
		super().__init__(*args, **kwargs)
		print()
		print("InitPrintBlock.__init__(",",".join(map(str,args)),kwargs.keys(),")")
