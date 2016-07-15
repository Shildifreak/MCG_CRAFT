# A voxelengine setup file contains all information that is game specific but important to the client

{
"CHUNKSIZE" : 3, # (in bit -> length is 2**CHUNKSIZE)
"TEXTURE_SIDE_LENGTH" : 4,
"DEFAULT_FOCUS_DISTANCE" : 8,
"TEXTURE_PATH" : "colors_texture.png",
"TEXTURE_EDGE_CUTTING" : 0.1, #value between 0 and 0.5 -> how much to cut away from the sides of each texture

#["Name",              transparenz, solid, ( oben), (unten), (seiten)]
"TEXTURE_INFO" : [
["BLACK",                    False,  True, ( 0, 0), ( 0, 0), ( 0, 0) ], #block ==  1
["WHITE",                    False,  True, ( 1, 0), ( 1, 0), ( 1, 0) ], #block ==  2
["RED",                      False,  True, ( 2, 0), ( 2, 0), ( 2, 0) ], #block ==  3
["GREEN",                    False,  True, ( 3, 0), ( 3, 0), ( 3, 0) ], #block ==  4
["BLUE",                     False,  True, ( 0, 1), ( 0, 1), ( 0, 1) ], #block ==  5
["YELLOW",                   False,  True, ( 1, 1), ( 1, 1), ( 1, 1) ], #block ==  6
["CYAN",                     False,  True, ( 2, 1), ( 2, 1), ( 2, 1) ], #block ==  7
["MAGENTA",                  False,  True, ( 3, 1), ( 3, 1), ( 3, 1) ], #block ==  8
]
}