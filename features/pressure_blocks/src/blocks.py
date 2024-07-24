from resources import *

@register_block("COMPRESSED_AIR")
class AirBlock(Block):
	defaults = Block.defaults.copy()
	defaults["pressure"] = 1

	def get_tags(self):
		return set() # no solid tag, no explosion tag
	def collides_with(self,area):
		return False


@register_block("GELB")
@register_block("HELLGRUN")
@register_block("GRUN")
@register_block("TURKIES")
@register_block("DUNKELGRUN")
@register_block("DUNKELGRAU")
@register_block("LILA")
@register_block("GRAU")
@register_block("ROT")
@register_block("HELLROT")
@register_block("ROSA")
@register_block("SCHWARZ")
@register_block("BRAUN")
@register_block("ORANGE")
@register_block("HELLORANGE")
@register_block("HELLBLAU")
@register_block("HELLGRAU")
@register_block("WEISS")
class MovableBlock(Block):
	pass

