# A voxelengine setup file contains all information that is game specific but important to the client

{
"CHUNKSIZE" : 3, # (in bit -> length is 2**CHUNKSIZE)
"TEXTURE_SIDE_LENGTH" : 16,
"DEFAULT_FOCUS_DISTANCE" : 8,
"TEXTURE_PATH" : "mc_texture.png",

   #["Name",               transparenz, solid, [( oben), (unten), ( rest)]],
   #  oder
   #["Name",               transparenz, solid, [( oben), (unten), ( nord), ( sued), ( west), ( ost)]],
"TEXTURE_INFO" : [
    ["GRASS",                    False,  True, [( 0, 2), ( 0, 0), ( 0, 1)]],
    ["SAND",                     False,  True, [( 1, 0), ( 1, 0), ( 1, 0)]],
    ["BRICK",                    False,  True, [( 3, 0), ( 3, 0), ( 3, 0)]],
    ["STONE",                    False,  True, [( 2, 0), ( 2, 0), ( 2, 0)]],
    ["DIRT",                     False,  True, [( 0, 0), ( 0, 0), ( 0, 0)]],
    ["STEIN",                    False,  True, [( 5, 0), ( 5, 0), ( 5, 0)]],
    ["HOLZ",                     False,  True, [( 4, 0), ( 4, 0), ( 4, 1)]],
    ["LAUB",                     False,  True, [(14, 0), (14, 0), (14, 0)]],
    ["GREEN" ,                   False,  True, [( 0, 2), ( 0, 2), ( 0, 2)]],
    ["HOLZBRETTER" ,             False,  True, [( 7, 0), ( 7, 0), ( 7, 0)]],
    #bis hier INVENTAR 1
    ["BRUCHSTEIN" ,              False,  True, [(10, 0), (10, 0), (10, 0)]],
    ["SCHNEEERDE" ,              False,  True, [( 8, 2), ( 0, 0), ( 8, 1)]],
    ["SCHNEE" ,                  False,  True, [(15, 0), (15, 0), (15, 0)]],
    ["WOLLE" ,                   False,  True, [( 8, 2), ( 8, 2), ( 8, 2)]],
    ["STEINZIEGEL" ,             False,  True, [(12, 0), (12, 0), (12, 0)]],
    ["SCHILDBLOCK" ,             False,  True, [(13, 0), (13, 0), (13, 0)]],

    #bis hier INVENTAR 2
    ["GELB" ,                    False,  True, [( 0,11), ( 0,11), ( 0,11)]],
    ["HELLGRUN" ,                False,  True, [( 1,11), ( 1,11), ( 1,11)]],
    ["GRUN" ,                    False,  True, [( 2,11), ( 2,11), ( 2,11)]],
    ["TURKIES" ,                 False,  True, [( 3,11), ( 3,11), ( 3,11)]],
    ["SCHWARZ" ,                 False,  True, [( 0,12), ( 0,12), ( 0,12)]],
    ["LILA" ,                    False,  True, [( 7,11), ( 7,11), ( 7,11)]],
    ["ORANGE" ,                  False,  True, [( 5,12), ( 5,12), ( 5,12)]],
    ["HELLBLAU" ,                False,  True, [(11,12), (11,12), (11,12)]],
    ["ROT" ,                     False,  True, [(11,11), (11,11), (11,11)]],
    ["HELLROT" ,                 False,  True, [(12,11), (12,11), (12,11)]],
    ["ROSA" ,                    False,  True, [(13,11), (13,11), (13,11)]],
    ["HELLGRAU",                 False,  True, [(12,12), (12,12), (12,12)]],
    ["DUNKELGRUN" ,              False,  True, [( 4,11), ( 4,11), ( 4,11)]],
    ["GRAU" ,                    False,  True, [( 8,11), ( 8,11), ( 8,11)]],
    ["DUNKELGRAU" ,              False,  True, [( 6,11), ( 6,11), ( 6,11)]],
    ["HELLORANGE" ,              False,  True, [( 6,12), ( 6,12), ( 6,12)]],
    ["BRAUN" ,                   False,  True, [( 3,12), ( 3,12), ( 3,12)]],
    #bis hier INVENTAR FARBEN

    ["DIAMANT" ,                 False,  True, [( 6, 2), ( 6, 2), ( 6, 2)]],
    ["REDSTONE" ,                False,  True, [( 7, 2), ( 7, 2), ( 7, 2)]],
    ["GOLD" ,                    False,  True, [( 5, 2), ( 5, 2), ( 5, 2)]],
    ["GOLDERZ" ,                 False,  True, [( 3, 2), ( 3, 2), ( 3, 2)]],
    ["IRON" ,                    False,  True, [( 6, 1), ( 6, 1), (11, 0)]],
    ["SMARAGTBLOCK" ,            False,  True, [( 1, 1), ( 1, 1), ( 1, 1)]],
    ["SMARAGTERZ" ,              False,  True, [( 2, 2), ( 2, 2), ( 2, 2)]],
    ["DIAMANTERZ" ,              False,  True, [( 2, 1), ( 2, 1), ( 2, 1)]],
    ["EISENERZ" ,                False,  True, [( 7, 1), ( 7, 1), ( 7, 1)]],
    ["KOHLEERZ" ,                False,  True, [( 1, 2), ( 1, 2), ( 1, 2)]],
    ["Quarzsaule",               False,  True, [( 9, 2), ( 9, 2), ( 9, 1)]],
    #Erze
    ["GESICHT" ,                 False,  True, [( 1,15), (1 ,15), ( 2,14), ( 0,14), ( 3,14), ( 1,14)]],
    ["CREEPER" ,                 False,  True, [( 3,13), (3 ,13), ( 2,13)]],
    ["Zombie" ,                  False,  True, [( 1,15), (1 ,15), ( 0,13)]],
    ["Skelett",                  False,  True, [(15, 0), (15, 0), ( 0,15)]],
    # Gesichter
    ["Commandblock",             False,  True, [(10, 1), (10, 1), (10, 1)]],
    ["Fruhlingsgrass",           False,  True, [( 7, 3), ( 0, 0), ( 0, 1)]],
    ["Fruhlingslaub",            False,  True, [(11, 1), (11, 1), (11, 1)]],
    ["GLAS",                     False,  True, [( 9, 0), ( 9, 0), ( 9, 0)]],
    ["TNT",                      False,  True, [(14, 1), (14, 1), (15, 1)]],
    ["Netherstone",              False,  True, [( 7, 4), ( 7, 4), ( 7, 4)]],
    ["Lapiserz",                 False,  True, [( 7, 3), ( 7, 3), ( 7, 3)]],
    ["Bucherregal",              False,  True, [( 7, 0), ( 7, 0), (15, 2)]],
    ["Obsidian" ,                False,  True, [( 9, 4), ( 9, 4), ( 9, 4)]],
    ["Prismarin",                False,  True, [(14, 7), (14, 7), (14, 7)]],
    ["Myzeln",                   False,  True, [( 9, 5), ( 0, 0), ( 8, 5)]],
    ["Rissige_Steinziegel",      False,  True, [(11, 6), (11, 6), (11, 6)]],    
    ["Steinziegel",              False,  True, [(11, 8), (11, 8), (11, 8)]],
    ["Gemeisselter_Steinziegel", False,  True, [(11, 7), (11, 7), (11, 7)]],
    ],

"ENTITY_MODELS": {
    "PLAYER":{
        "head":[((0,-0.6,0),(0,0.6,0),(1,1,1),"GESICHT")],
        "body":[((0,-1,0),(0,0,0),(0.8,1,0.4),"<<random>>")],
        }
    },

}
