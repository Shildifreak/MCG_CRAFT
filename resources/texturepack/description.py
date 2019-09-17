# A texturepack file contains all information that is game specific and important to the client

{
"TEXTURE_SIDE_LENGTH" : 16,
#"TEXTURE_EDGE_CUTTING" : 0.1, #value between 0 and 0.5 -> how much to cut away from the sides of each texture

   #["Name",               transparenz,    icon, [( oben), (unten), ( vorne), ( hinten), ( links), ( rechts)]],
"TEXTURE_INFO" : [
    ["GRASS",                    False,       2, [( 0, 2), ( 0, 0), ( 0, 1)]],
    ["SAND",                     False,       0, [( 1, 0)]],
    ["BRICK",                    False,       0, [( 3, 0)]],
    ["BEDROCK",                  False,       0, [( 2, 0)]],
    ["DIRT",                     False,       0, [( 0, 0)]],
    ["STONE",                    False,       0, [( 5, 0)]],
    ["HOLZ",                     False,       0, [( 4, 0), ( 4, 0), ( 4, 1)]],
    ["LAUB",                     True ,       0, [(14, 0)]],
    ["GREEN" ,                   False,       0, [( 0, 2)]],
    ["HOLZBRETTER" ,             False,       0, [( 7, 0)]],
    #bis hier INVENTAR 1
    ["BRUCHSTEIN" ,              False,       0, [(10, 0)]],
    ["SCHNEEERDE" ,              False,       0, [( 8, 2), ( 0, 0), ( 8, 1)]],
    ["SCHNEE" ,                  False,       0, [(15, 0)]],
    ["WOLLE" ,                   False,       0, [( 8, 2)]],
    ["STEINZIEGEL" ,             False,       0, [(12, 0)]],
    ["SCHILDBLOCK" ,             False,       0, [(13, 0)]],

    #bis hier INVENTAR 2
    ["GELB" ,                    False,       0, [( 0,11)]],
    ["HELLGRUN" ,                False,       0, [( 1,11)]],
    ["GRUN" ,                    False,       0, [( 2,11)]],
    ["TURKIES" ,                 False,       0, [( 3,11)]],
    ["SCHWARZ" ,                 False,       0, [( 0,12)]],
    ["LILA" ,                    False,       0, [( 7,11)]],
    ["ORANGE" ,                  False,       0, [( 5,12)]],
    ["HELLBLAU" ,                False,       0, [(11,12)]],
    ["ROT" ,                     False,       0, [(11,11)]],
    ["HELLROT" ,                 False,       0, [(12,11)]],
    ["ÖL",                       False,       0, [( 1, 5)]],
    ["ROSA" ,                    False,       0, [(13,11)]],
    ["HELLGRAU",                 False,       0, [(12,12)]],
    ["DUNKELGRUN" ,              False,       0, [( 4,11)]],
    ["GRAU" ,                    False,       0, [( 8,11)]],
    ["DUNKELGRAU" ,              False,       0, [( 6,11)]],
    ["HELLORANGE" ,              False,       0, [( 6,12)]],
    ["BRAUN" ,                   False,       0, [( 3,12)]],
    ["WEISS" ,                   False,       0, [(13,12)]],
    #bis hier INVENTAR FARBEN

    ["Muenzen",                  False,       0, [( 1, 4)]],
    ["Scheine",                  False,       0, [( 2, 4)]],
    ["Kredidtkarte",             False,       0, [( 0, 4)]],
    #Gegenstände
    
    ["DIAMANT" ,                 False,       0, [( 6, 2)]],
    ["REDSTONE" ,                False,       0, [( 7, 2)]],
    ["GOLD" ,                    False,       0, [( 5, 2)]],
    ["GOLDERZ" ,                 False,       0, [( 3, 2)]],
    ["IRON" ,                    False,       0, [( 6, 1), ( 6, 1), (11, 0)]],
    ["SMARAGTBLOCK" ,            False,       0, [( 1, 1)]],
    ["SMARAGTERZ" ,              False,       0, [( 2, 2)]],
    ["DIAMANTERZ" ,              False,       0, [( 2, 1)]],
    ["EISENERZ" ,                False,       0, [( 7, 1)]],
    ["KOHLEERZ" ,                False,       0, [( 1, 2)]],
    ["Quarzsaule",               False,       0, [( 9, 2)]],
    #Erze                                     
    ["GESICHT" ,                 False,       2, [( 1,15), (1 ,15), ( 1,14), ( 3,14), ( 0,14), ( 2,14)]],
    ["CREEPER" ,                 False,       0, [( 3,13), (3 ,13), ( 2,13)]],
    ["Zombie" ,                  False,       0, [( 1,15), (1 ,15), ( 0,13)]],
    ["Skelett",                  False,       0, [(15, 0), (15, 0), ( 0,15)]],
    ["Schaf",                    False,       0, [(13,12), (13,12), ( 4,13), (13,12)]],
    ["Damengesicht",             False,       0, [(10,13), ( 4,12), ( 8,13), ( 9,13), (11,13), (11,13)]],
    ["Geist",                    False,       0, [(11,12), (10, 1), (13,13), (11,12)]],
    # Gesichter
    ["Schafbeine",               False,       0, [(13,12), ( 0,12), ( 5,13)]],
    ["Menschenbeine",            False,       0, [( 1,15), ( 1,15), ( 6,13)]],
    ["Damenbeine",               False,       0, [(15,11), (15,11), ( 7,13)]],
    # Beine
    ["Damenkoerper",              False,       0, [(12,13)]],
    #Oberkörper
    ["Commandblock",             False,       0, [(10, 1)]],
    ["Fruhlingsgrass",           False,       2, [( 7, 3), ( 0, 0), ( 0, 1)]],
    ["Fruhlingslaub",            False,       0, [(11, 1)]],
    ["GLAS",                     True,        0, [(12, 7)]],
    ["RACKETENWERFER",           False,       0, [(10, 9), (10, 9), (10, 9), (12, 9), (11, 9), (11, 9)]],  
    ["TNT",                      False,       2, [(14, 1), (14, 1), (15, 1)]],
    ["A-TNT",                    False,       2, [(13, 4), (12, 4), (14, 4)]],
    ["B-TNT",                    False,       2, [( 5, 4), ( 4, 4), ( 6, 4)]],
    ["Netherstone",              False,       0, [( 7, 4)]],
    ["Lapiserz",                 False,       0, [( 7, 3)]],
    ["Bucherregal",              False,       2, [( 7, 0), ( 7, 0), (15, 2)]],
    ["Obsidian" ,                False,       0, [( 9, 4)]],
    ["Prismarin",                False,       0, [(14, 7)]],
    ["Myzeln",                   False,       2, [( 9, 5), ( 0, 0), ( 8, 5)]],
    ["Rissige_Steinziegel",      False,       0, [(11, 6)]],    
    ["Steinziegel",              False,       0, [(11, 8)]],
    ["Gemeisselter_Steinziegel", False,       0, [(11, 7)]],
    ["CHEST",                    False,       2, [(15, 9), (14, 9), (14,10), (15,10), (15,10), (15,10)]],
    ["missing_texture",          False,       0, [(15,15)]],
    ["HERZ",                     True ,       1, [(14,15), (12, 6), (14,15)]], 
    ["DOORTOP",                  False,       0, [(10, 6), (10, 6), (10, 8)]],
    ["DOORSTEP",                 False,       0, [(10, 6)]],
    ["DOORBOTTOM",               False,       0, [(10, 6), (10, 6), (10, 7)]],
    ["DOORTOPOPEN",              True,        0, [( 9, 6), (14,15), ( 9, 8)]],
    ["DOORBOTTOMOPEN",           True,        0, [(14,15), ( 9, 6), ( 9, 7)]],
    ["BARRIER",                  True,        0, [(14,15)]],
    ["WAND",                     False,       0, [( 2,11)]],
    ["TORCH",                    True,        0, [( 7, 5)]],
    ["LAMP",                     False,       0, [( 6,10)]],
    ["LAMPOFF",                  False,       0, [( 6,10)]],
    ["LAMPON",                   False,       0, [( 7,10)]],
    ["Redstone",                 False,       0, [( 7, 2)]],
    ["FAN",                      False,       0, [( 8,10), ( 0,10)]],
    ["Repeater",                 True,        1, [(14,15), ( 6, 5), (14,15)]],
    ["AIM",                      False,       0, [(15,11)]],
    ],

"BLOCK_MODELS": [
    ["Setzling",                 True , ( 3, 4), [[],[],[],[],[],[],[(0,0,0, 1,0,1, 1,1,1, 0,1,0),(0,0,1, 1,0,0, 1,1,0, 0,1,1)]],
                                                 [[],[],[],[],[],[],[( 3, 4)                     ,( 3, 4)                     ]]],
    ["GLAS",                     True , (12, 7), [[(0,1,1, 1,1,1, 1,1,0, 0,1,0)], [(1,0,1, 0,0,1, 0,0,0, 1,0,0)], [(0,0,1, 1,0,1, 1,1,1, 0,1,1)], [(1,0,0, 0,0,0, 0,1,0, 1,1,0)], [(0,0,0, 0,0,1, 0,1,1, 0,1,0)], [(1,0,1, 1,0,0, 1,1,0, 1,1,1)],[]],
                                                 [[(12, 7)],                      [(12, 7)],                      [(12, 7)],                      [(12, 7)],                      [(12, 7)],                      [(12, 7)],                     []]],
    ["HEBEL",                    True , ( 5,10), [[],[],[(1,0,1, 0,0,1, 0,0.5,1, 1,0.5,1)],[(0,0,0, 1,0,0, 1,0.5,0, 0,0.5,0)],[(0,0,1, 0,0,0, 0,0.5,0, 0,0.5,1)],[(1,0,0, 1,0,1, 1,0.5,1, 1,0.5,0)],[(0,0.5,0, 1,0.5,0, 1,0.5,1, 0,0.5,1), (0.375,0,1, 0.375,1,0, 0.625,1,0, 0.625,0,1)]],
                                                 [[],[],[(10,2,1,0.5)                    ],[(10,2,1,0.5)                    ],[(10,2,1,0.5)                    ],[(10,2,1,0.5)                    ],[(12, 0)                             , ( 4, 1, 1, 0.25)]]],
    ["grass",                    True , ( 0, 3), [[],[],[],[],[],[],[(0,0,0, 1,0,1, 1,1,1, 0,1,0),(0,0,1, 1,0,0, 1,1,0, 0,1,1)]],
                                                 [[],[],[],[],[],[],[( 0, 3)                     ,( 0, 3)                     ]]],
    ["WeisseBlume",              True , ( 5, 3), [[],[],[],[],[],[],[(0,0,0, 1,0,1, 1,1,1, 0,1,0),(0,0,1, 1,0,0, 1,1,0, 0,1,1)]],
                                                 [[],[],[],[],[],[],[( 5, 3)                     ,( 5, 3)                     ]]],
    ["LilaBlume",                True , ( 3, 3), [[],[],[],[],[],[],[(0,0,0, 1,0,1, 1,1,1, 0,1,0),(0,0,1, 1,0,0, 1,1,0, 0,1,1)]],
                                                 [[],[],[],[],[],[],[( 3, 3)                     ,( 3, 3)                     ]]],
    ["RoteBlume",                True , ( 2, 3), [[],[],[],[],[],[],[(0,0,0, 1,0,1, 1,1,1, 0,1,0),(0,0,1, 1,0,0, 1,1,0, 0,1,1)]],
                                                 [[],[],[],[],[],[],[( 2, 3)                     ,( 2, 3)                     ]]],
    ["GelbeBlume",               True , ( 1, 3), [[],[],[],[],[],[],[(0,0,0, 1,0,1, 1,1,1, 0,1,0),(0,0,1, 1,0,0, 1,1,0, 0,1,1)]],
                                                 [[],[],[],[],[],[],[( 1, 3)                     ,( 1, 3)                     ]]],
    ["SonnenBlume",              True , ( 4, 3), [[],[],[],[],[],[],[(0,0,0, 1,0,1, 1,1,1, 0,1,0),(0,0,1, 1,0,0, 1,1,0, 0,1,1)]],
                                                 [[],[],[],[],[],[],[( 4, 3)                     ,( 4, 3)                     ]]],
    ["BlaueBlume",               True , ( 6, 3), [[],[],[],[],[],[],[(0,0,0, 1,0,1, 1,1,1, 0,1,0),(0,0,1, 1,0,0, 1,1,0, 0,1,1)]],
                                                 [[],[],[],[],[],[],[( 6, 3)                     ,( 6, 3)                     ]]],
    ["TORCHON",                  True , ( 7, 5), [[],[],[],[],[],[],[(0,0,0.5, 1,0,0.5, 1,1,0.5, 0,1,0.5),(0.5,0,0, 0.5,0,1, 0.5,1,1, 0.5,1,0)]],
                                                 [[],[],[],[],[],[],[( 7, 5, 1, 1)                        ,( 7, 5, 1, 1)                      ]]],
    ["TORCHOFF",                 True , ( 7, 5), [[],[],[],[],[],[],[(0,0,0.5, 1,0,0.5, 1,1,0.5, 0,1,0.5),(0.5,0,0, 0.5,0,1, 0.5,1,1, 0.5,1,0)]],
                                                 [[],[],[],[],[],[],[( 7, 6, 1, 1)                        ,( 7, 6, 1, 1)                      ]]],
    ["ROCKET",                   True , (13, 9), [[],[],[],[],[],[],[(0.5,0,0, 0.5,0,1, 0.5,1,1, 0.5,1,0),(1,0.5,0, 1,0.5,1, 0,0.5,1, 0,0.5,0)]],
                                                 [[],[],[],[],[],[],[(13, 9),                              (13, 9)]]],
    ['Redstone0', True, (7, 2), [[], [], [], [], [], [], [(0.375, 0.1, 0, 0.625, 0.1, 0, 0.625, 0.1, 1, 0.375, 0.1, 1), (1, 0.1, 0.375, 1, 0.1, 0.625, 0, 0.1, 0.625, 0, 0.1, 0.375)]], [[], [], [], [], [], [], [(3.75, 9, 0.25, 1), (3.75, 9, 0.25, 1)]]], ['Redstone1', True, (7, 2), [[], [], [], [], [], [], [(0.375, 0.1, 0, 0.625, 0.1, 0, 0.625, 0.1, 1, 0.375, 0.1, 1), (1, 0.1, 0.375, 1, 0.1, 0.625, 0, 0.1, 0.625, 0, 0.1, 0.375)]], [[], [], [], [], [], [], [(3.5, 9, 0.25, 1), (3.5, 9, 0.25, 1)]]], ['Redstone2', True, (7, 2), [[], [], [], [], [], [], [(0.375, 0.1, 0, 0.625, 0.1, 0, 0.625, 0.1, 1, 0.375, 0.1, 1), (1, 0.1, 0.375, 1, 0.1, 0.625, 0, 0.1, 0.625, 0, 0.1, 0.375)]], [[], [], [], [], [], [], [(3.25, 9, 0.25, 1), (3.25, 9, 0.25, 1)]]], ['Redstone3', True, (7, 2), [[], [], [], [], [], [], [(0.375, 0.1, 0, 0.625, 0.1, 0, 0.625, 0.1, 1, 0.375, 0.1, 1), (1, 0.1, 0.375, 1, 0.1, 0.625, 0, 0.1, 0.625, 0, 0.1, 0.375)]], [[], [], [], [], [], [], [(3.0, 9, 0.25, 1), (3.0, 9, 0.25, 1)]]], ['Redstone4', True, (7, 2), [[], [], [], [], [], [], [(0.375, 0.1, 0, 0.625, 0.1, 0, 0.625, 0.1, 1, 0.375, 0.1, 1), (1, 0.1, 0.375, 1, 0.1, 0.625, 0, 0.1, 0.625, 0, 0.1, 0.375)]], [[], [], [], [], [], [], [(2.75, 9, 0.25, 1), (2.75, 9, 0.25, 1)]]], ['Redstone5', True, (7, 2), [[], [], [], [], [], [], [(0.375, 0.1, 0, 0.625, 0.1, 0, 0.625, 0.1, 1, 0.375, 0.1, 1), (1, 0.1, 0.375, 1, 0.1, 0.625, 0, 0.1, 0.625, 0, 0.1, 0.375)]], [[], [], [], [], [], [], [(2.5, 9, 0.25, 1), (2.5, 9, 0.25, 1)]]], ['Redstone6', True, (7, 2), [[], [], [], [], [], [], [(0.375, 0.1, 0, 0.625, 0.1, 0, 0.625, 0.1, 1, 0.375, 0.1, 1), (1, 0.1, 0.375, 1, 0.1, 0.625, 0, 0.1, 0.625, 0, 0.1, 0.375)]], [[], [], [], [], [], [], [(2.25, 9, 0.25, 1), (2.25, 9, 0.25, 1)]]], ['Redstone7', True, (7, 2), [[], [], [], [], [], [], [(0.375, 0.1, 0, 0.625, 0.1, 0, 0.625, 0.1, 1, 0.375, 0.1, 1), (1, 0.1, 0.375, 1, 0.1, 0.625, 0, 0.1, 0.625, 0, 0.1, 0.375)]], [[], [], [], [], [], [], [(2.0, 9, 0.25, 1), (2.0, 9, 0.25, 1)]]], ['Redstone8', True, (7, 2), [[], [], [], [], [], [], [(0.375, 0.1, 0, 0.625, 0.1, 0, 0.625, 0.1, 1, 0.375, 0.1, 1), (1, 0.1, 0.375, 1, 0.1, 0.625, 0, 0.1, 0.625, 0, 0.1, 0.375)]], [[], [], [], [], [], [], [(1.75, 9, 0.25, 1), (1.75, 9, 0.25, 1)]]], ['Redstone9', True, (7, 2), [[], [], [], [], [], [], [(0.375, 0.1, 0, 0.625, 0.1, 0, 0.625, 0.1, 1, 0.375, 0.1, 1), (1, 0.1, 0.375, 1, 0.1, 0.625, 0, 0.1, 0.625, 0, 0.1, 0.375)]], [[], [], [], [], [], [], [(1.5, 9, 0.25, 1), (1.5, 9, 0.25, 1)]]], ['Redstone10', True, (7, 2), [[], [], [], [], [], [], [(0.375, 0.1, 0, 0.625, 0.1, 0, 0.625, 0.1, 1, 0.375, 0.1, 1), (1, 0.1, 0.375, 1, 0.1, 0.625, 0, 0.1, 0.625, 0, 0.1, 0.375)]], [[], [], [], [], [], [], [(1.25, 9, 0.25, 1), (1.25, 9, 0.25, 1)]]], ['Redstone11', True, (7, 2), [[], [], [], [], [], [], [(0.375, 0.1, 0, 0.625, 0.1, 0, 0.625, 0.1, 1, 0.375, 0.1, 1), (1, 0.1, 0.375, 1, 0.1, 0.625, 0, 0.1, 0.625, 0, 0.1, 0.375)]], [[], [], [], [], [], [], [(1.0, 9, 0.25, 1), (1.0, 9, 0.25, 1)]]], ['Redstone12', True, (7, 2), [[], [], [], [], [], [], [(0.375, 0.1, 0, 0.625, 0.1, 0, 0.625, 0.1, 1, 0.375, 0.1, 1), (1, 0.1, 0.375, 1, 0.1, 0.625, 0, 0.1, 0.625, 0, 0.1, 0.375)]], [[], [], [], [], [], [], [(0.75, 9, 0.25, 1), (0.75, 9, 0.25, 1)]]], ['Redstone13', True, (7, 2), [[], [], [], [], [], [], [(0.375, 0.1, 0, 0.625, 0.1, 0, 0.625, 0.1, 1, 0.375, 0.1, 1), (1, 0.1, 0.375, 1, 0.1, 0.625, 0, 0.1, 0.625, 0, 0.1, 0.375)]], [[], [], [], [], [], [], [(0.5, 9, 0.25, 1), (0.5, 9, 0.25, 1)]]], ['Redstone14', True, (7, 2), [[], [], [], [], [], [], [(0.375, 0.1, 0, 0.625, 0.1, 0, 0.625, 0.1, 1, 0.375, 0.1, 1), (1, 0.1, 0.375, 1, 0.1, 0.625, 0, 0.1, 0.625, 0, 0.1, 0.375)]], [[], [], [], [], [], [], [(0.25, 9, 0.25, 1), (0.25, 9, 0.25, 1)]]], ['Redstone15', True, (7, 2), [[], [], [], [], [], [], [(0.375, 0.1, 0, 0.625, 0.1, 0, 0.625, 0.1, 1, 0.375, 0.1, 1), (1, 0.1, 0.375, 1, 0.1, 0.625, 0, 0.1, 0.625, 0, 0.1, 0.375)]], [[], [], [], [], [], [], [(0.0, 9, 0.25, 1), (0.0, 9, 0.25, 1)]]]
    #["Repeater0On",              True ,        , [[],[],[],[],[],[],[(0,0.1,0,0,0.1,1,1,0.1,1,1,0.1,0),
    ],

"ENTITY_MODELS": {
    "MENSCH":{
        "head":[((0,-0.6,0),(0,0.6,0),(1,1,1),"GESICHT:2")],
        "body":[((0,-0.7,0),(0,0,0),(1,0.4,0.6),"<<random>>")],
        "legl":[],#((0.3,0,0),(0,0,0),(0.4,0.6,0.4),"Menschenbeine")],
        "legr":[],#((-0.3,0,0),(0,0,0),(0.4,0.6,0.4),"Menschenbeine")],
        },
    "SCHAF":{
        "head":[((0,0,0),(0,0.8,-0.75),(0.7,0.7,0.6),"Schaf:2")],
        "body":[((0,0,0),(0,0,0),(1.1,1.1,1.7),"WEISS"),
                ((0,0,0),(0,0.1,0.9),(0.3,0.4,0.2),"WEISS")],
        "legl":[((0.35,-0.3,0.55),(0,-0.5,0),(0.35,1,0.35),"Schafbeine"),
                ((0.35,-0.3,-0.55),(0,-0.5,0),(0.35,1,0.35),"Schafbeine")],
        "legr":[((-0.35,-0.3,-0.55),(0,-0.5,0),(0.35,1,0.35),"Schafbeine"),
                ((-0.35,-0.3,0.55),(0,-0.5,0),(0.35,1,0.35),"Schafbeine")],
        },
    "EINHORN":{
        "head":[],
        "body":[],
        "legl":[],
        "legr":[],
        },
    "DAME":{
        "head":[((0,0,0),(0,1,0),(1,1,1),"Damengesicht:2")],
        "body":[((0,0,0),(0,0,0),(1,1,1),"Damenkoerper")],
        "legl":[((0,0,0),(0.3,-1,0),(0.5,1,0.5),"Damenbeine"),   #Bein
                ((0,0,0),(0.8,0,0),(0.5,1,0.5),"Damenbeine")],  #Arm
        "legr":[((0,0,0),(-0.3,-1,0),(0.5,1,0.5),"Damenbeine")],
        },
    "GEIST":{
        "head":[((0,0,0),(0,0,0),(3,3,3),"Geist")],
        "body":[],
        "legl":[],
        "legr":[],
        },
    },

}
