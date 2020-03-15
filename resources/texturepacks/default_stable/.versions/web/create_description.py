data = {
	"blockDataArray" : [
		#   -x   x      -y   y      -z   z     r g b a
		0x00000000, 0x00000000, 0x00000000, 0x00000000, # Air
		0x00010001, 0x00010001, 0x00010001, 0x00000000, # Stone
		0x00020002, 0x00020002, 0x00020002, 0x00000000, # Box
		0x00050005, 0x00050005, 0x00050005, 0x00000000, # Dirt
		0x00000000, 0x00000006, 0x00000000, 0x88AAFF88, # Water
#		0x00060006, 0x00060006, 0x00060006, 0x88AAFF88, # Water
		0x00040004, 0x00050003, 0x00040004, 0x00000000, # Grass
		0x00070007, 0x00070007, 0x00070007, 0x00000000, # Leaves
		0x00080008, 0x00080008, 0x00080008, 0x00000000, # Diamond
		0x000A000A, 0x00090009, 0x000A000A, 0x00000000, # Log
		0x000E000E, 0x000E000E, 0x000E000E, 0x00000000, # Mirror
		0x000C000C, 0x000D000B, 0x000C000C, 0x00000000, # Crafting Bench
	]
}

import json
with open("description.json","w") as f:
	json.dump(data,f)
