# A voxelengine setup file contains all information that is game specific but important to the client

{
"TEXTURE_SIDE_LENGTH" : 4,
"TEXTURE_EDGE_CUTTING" : 0.1, #value between 0 and 0.5 -> how much to cut away from the sides of each texture

#["Name",              transparenz, solid, [( oben), (unten), (seiten)]]
"TEXTURE_INFO" : [
["BLACK",                    False,  True, [( 0, 0), ( 0, 0), ( 0, 0) ]],
["WHITE",                    False,  True, [( 1, 0), ( 1, 0), ( 1, 0) ]],
["RED",                      False,  True, [( 2, 0), ( 2, 0), ( 2, 0) ]],
["GREEN",                    False,  True, [( 3, 0), ( 3, 0), ( 3, 0) ]],
["BLUE",                     False,  True, [( 0, 1), ( 0, 1), ( 0, 1) ]],
["YELLOW",                   False,  True, [( 1, 1), ( 1, 1), ( 1, 1) ]],
["CYAN",                     False,  True, [( 2, 1), ( 2, 1), ( 2, 1) ]],
["MAGENTA",                  False,  True, [( 3, 1), ( 3, 1), ( 3, 1) ]],
["GREY",                     False,  True, [( 0, 2), ( 0, 2), ( 0, 2) ]],
],

"BLOCK_MODELS":[],
"ENTITY_MODELS":{},
}
