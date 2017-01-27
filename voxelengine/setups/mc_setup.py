# A voxelengine setup file contains all information that is game specific but important to the client

{
"CHUNKSIZE" : 3, # (in bit -> length is 2**CHUNKSIZE)
"TEXTURE_SIDE_LENGTH" : 16,
"DEFAULT_FOCUS_DISTANCE" : 8,
"TEXTURE_PATH" : "mc_texture.png",

   #["Name",               transparenz, solid, ( oben), (unten), (seiten)],
"TEXTURE_INFO" : [
    ["GRASS",                    False,  True, ( 0, 2), ( 0, 0), ( 0, 1)], #block ==  1
    ["SAND",                     False,  True, ( 1, 0), ( 1, 0), ( 1, 0)], #block ==  2
    ["BRICK",                    False,  True, ( 3, 0), ( 3, 0), ( 3, 0)], #block ==  3
    ["STONE",                    False,  True, ( 2, 0), ( 2, 0), ( 2, 0)], #block ==  4
    ["DIRT",                     False,  True, ( 0, 0), ( 0, 0), ( 0, 0)], #block ==  5
    ["STEIN",                    False,  True, ( 5, 0), ( 5, 0), ( 5, 0)], #block ==  6
    ["HOLZ",                     False,  True, ( 4, 0), ( 4, 0), ( 4, 1)], #block ==  7
    ["LAUB",                     False,  True, (14, 0), (14, 0), (14, 0)], #block ==  8
    ["GREEN" ,                   False,  True, ( 0, 2), ( 0, 2), ( 0, 2)], #block ==  9
    ["HOLZBRETTER" ,             False,  True, ( 7, 0), ( 7, 0), ( 7, 0)], #block == 10
    #bis hier INVENTAR 1
    ["BRUCHSTEIN" ,              False,  True, (10, 0), (10, 0), (10, 0)], #block == 11
    ["SCHNEEERDE" ,              False,  True, ( 8, 2), ( 0, 0), ( 8, 1)], #block == 12
    ["SCHNEE" ,                  False,  True, (15, 0), (15, 0), (15, 0)], #block == 13
    ["WOLLE" ,                   False,  True, ( 8, 2), ( 8, 2), ( 8, 2)], #block == 14
    ["STEINZIEGEL" ,             False,  True, (12, 0), (12, 0), (12, 0)], #block == 15
    ["SCHILDBLOCK" ,             False,  True, (13, 0), (13, 0), (13, 0)], #block == 16

    #bis hier INVENTAR 2
    ["GELB" ,                    False,  True, ( 0,11), ( 0,11), ( 0,11)], #block == 17
    ["HELLGRUN" ,                False,  True, ( 1,11), ( 1,11), ( 1,11)], #block == 18
    ["GRUN" ,                    False,  True, ( 2,11), ( 2,11), ( 2,11)], #block == 19
    ["TURKIES" ,                 False,  True, ( 3,11), ( 3,11), ( 3,11)], #block == 20
    ["SCHWARZ" ,                 False,  True, ( 0,12), ( 0,12), ( 0,12)], #block == 21
    ["LILA" ,                    False,  True, ( 7,11), ( 7,11), ( 7,11)], #block == 22
    ["ORANGE" ,                  False,  True, ( 5,12), ( 5,12), ( 5,12)], #block == 23
    ["HELLBLAU" ,                False,  True, (11,12), (11,12), (11,12)], #block == 24
    ["ROT" ,                     False,  True, (11,11), (11,11), (11,11)], #block == 25
    ["HELLROT" ,                 False,  True, (12,11), (12,11), (12,11)], #block == 26
    ["ROSA" ,                    False,  True, (13,11), (13,11), (13,11)], #block == 27
    ["HELLGRAU",                 False,  True, (12,12), (12,12), (12,12)], #block == 28
    ["DUNKELGRUN" ,              False,  True, ( 4,11), ( 4,11), ( 4,11)], #block == 29
    ["GRAU" ,                    False,  True, ( 8,11), ( 8,11), ( 8,11)], #block == 30
    ["DUNKELGRAU" ,              False,  True, ( 6,11), ( 6,11), ( 6,11)], #block == 31
    ["HELLORANGE" ,              False,  True, ( 6,12), ( 6,12), ( 6,12)], #block == 32
    ["BRAUN" ,                   False,  True, ( 3,12), ( 3,12), ( 3,12)], #block == 33
    #bis hier INVENTAR FARBEN

    ["DIAMANT" ,                 False,  True, ( 6, 2), ( 6, 2), ( 6, 2)], #block == 34
    ["REDSTONE" ,                False,  True, ( 7, 2), ( 7, 2), ( 7, 2)], #block == 35
    ["GOLD" ,                    False,  True, ( 5, 2), ( 5, 2), ( 5, 2)], #block == 36
    ["GOLDERZ" ,                 False,  True, ( 3, 2), ( 3, 2), ( 3, 2)], #block == 37
    ["IRON" ,                    False,  True, ( 6, 1), ( 6, 1), (11, 0)], #block == 38
    ["SMARAGTBLOCK" ,            False,  True, ( 1, 1), ( 1, 1), ( 1, 1)], #block == 39
    ["SMARAGTERZ" ,              False,  True, ( 2, 2), ( 2, 2), ( 2, 2)], #block == 40
    ["DIAMANTERZ" ,              False,  True, ( 2, 1), ( 2, 1), ( 2, 1)], #block == 41
    ["EISENERZ" ,                False,  True, ( 7, 1), ( 7, 1), ( 7, 1)], #block == 42
    ["KOHLEERZ" ,                False,  True, ( 1, 2), ( 1, 2), ( 1, 2)], #block == 43
    ["Quarzsaule",               False,  True, ( 9, 2), ( 9, 2), ( 9, 1)], #block == 44
    #Erze
    ["GESICHT" ,                 False,  True, ( 1,15), (1 ,15), ( 1,14)], #block == 45
    ["CREEPER" ,                 False,  True, ( 3,13), (3 ,13), ( 2,13)], #block == 46
    ["Zombie" ,                  False,  True, ( 1,15), (1 ,15), ( 0,13)], #block == 47
    ["Skelett",                  False,  True, (15, 0), (15, 0), ( 0,15)], #block == 48
    # Gesichter
    ["Commandblock",             False,  True, (10, 1), (10, 1), (10, 1)], #block == 49
    ["Fruhlingsgrass",           False,  True, ( 7, 3), ( 0, 0), ( 0, 1)], #block == 50
    ["Fruhlingslaub",            False,  True, (11, 1), (11, 1), (11, 1)], #block == 51
    ["GLAS",                     False,  True, ( 9, 0), ( 9, 0), ( 9, 0)], #Block == 52
    ["TNT",                      False,  True, (14, 1), (14, 1), (15, 1)], #Block == 53
    ["Netherstone",              False,  True, ( 7, 4), ( 7, 4), ( 7, 4)], #block == 54
    ["Lapiserz",                 False,  True, ( 7, 3), ( 7, 3), ( 7, 3)], #block == 55
    ["Bucherregal",              False,  True, ( 7, 0), ( 7, 0), (15, 2)], #block == 56
    ["Obsidian" ,                False,  True, ( 9, 4), ( 9, 4), ( 9, 4)], #block == 57
    ["Prismarin",                False,  True, (14, 7), (14, 7), (14, 7)], #block == 58
    ["Myzeln",                   False,  True, ( 9, 5), ( 0, 0), ( 8, 5)], #block == 59
    ["Rissige_Steinziegel",      False,  True, (11, 6), (11, 6), (11, 6)], #block == 60    
    ["Steinziegel",              False,  True, (11, 8), (11, 8), (11, 8)], #block == 61
    ["Gemeisselter_Steinziegel", False,  True, (11, 7), (11, 7), (11, 7)], #block == 62
    ],

"ENTITY_MODELS": {
    "PLAYER":{
        "head":[((0,-0.75,0),(0,0.25,0),(1,1,1),"GESICHT")],
        "body":[((0,-1.5,0),(0,0,0),(1,1,1),"<<random>>")],
        }
    },

}
