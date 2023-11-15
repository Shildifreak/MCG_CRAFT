# A texturepack contains all information that is game specific and important to the client

# example

#{
#	"NAME" : {
#		"icon" : "side",
#		
#		"faces" : {
#			"top" : "top",
#			"bottom" : "bottom",
#			#"front" : "side",
#			#"back" : "side",
#			#"left" : "side",
#			#"right" : "side",
#			"other" : "side",
#		}
#		
#		"transparent" : False,
#		"connecting" : False,
#		"fog_color" : (255,255,255,255),
#		
#		"refraction_index" : 1,
#       "translucency" : 0,
#		"color_filter": ((1, 0, 0, 0),
#						 (0, 1, 0, 0),
#						 (0, 0, 1, 0),
#						 (0, 0, 0, 1)),
#}


{
"BLOCKS" : {
    "missing_texture"          : {},

    # INVENTAR 1
    "SAND"                     : {"faces":{                                       "other":"sand"       }                      },
    "SANDSTEIN"                : {"faces":{"top":"sand",                          "other":"sandstone"  }, "icon":"sandstone"  },
    "BRICK"                    : {"faces":{                                       "other":"brick"      }                      },
    "BEDROCK"                  : {"faces":{                                       "other":"bedrock"    }                      },
    "DIRT"                     : {"faces":{                                       "other":"dirt"       }                      },
    "STONE"                    : {"faces":{                                       "other":"stone"      }                      },
    "MOSSSTONE"                : {"faces":{                                       "other":"mossstone"  }                      },
    "HOLZ"                     : {"faces":{"top":"hirnholz", "bottom":"hirnholz", "other":"holzrinde"  }                      },
    "LAUB"                     : {"faces":{                                       "other":"laub"       }, "transparent":True  },
    "HOLZBRETTER"              : {"faces":{                                       "other":"holzbretter"}                      },
                                                                                                         
    "GRASS"                    : {"faces":{"top":"grass_top", "bottom":"dirt",    "other":"grass_side" }, "icon":"grass_side" },
    "Myzeln"                   : {"faces":{"top":"myzel_top", "bottom":"dirt",    "other":"myzel_side" }, "icon":"myzel_side" },
    "SCHNEEERDE"               : {"faces":{"top":"schnee_top","bottom":"dirt",    "other":"schnee_side"}, "icon":"schnee_side"},

    # INVENTAR 2
    "BRUCHSTEIN"               : {"faces":{"all": "bruchstein" }},
    "SCHNEE"                   : {"faces":{"all": "schnee"     }},
    "SCHILDBLOCK"              : {"faces":{"all": "schildblock"}},

    # FARBEN
    "GELB"                     : {"faces":{"all": "gelb"             }},
    "HELLGRUN"                 : {"faces":{"all": "hellgrun"         }},
    "GRUN"                     : {"faces":{"all": "grun"             }},
    "TURKIES"                  : {"faces":{"all": "turkies"          }},
    "DUNKELGRUN"               : {"faces":{"all": "dunkelgrun"       }},
    "DUNKELGRAU"               : {"faces":{"all": "dunkelgrau"       }},
    "LILA"                     : {"faces":{"all": "lila"             }},
    "GRAU"                     : {"faces":{"all": "grau"             }},
    "ROT"                      : {"faces":{"all": "rot"              }},
    "HELLROT"                  : {"faces":{"all": "hellrot"          }},
    "ROSA"                     : {"faces":{"all": "rosa"             }},
    "SCHWARZ"                  : {"faces":{"all": "schwarz"          }},
    "BRAUN"                    : {"faces":{"all": "braun"            }},
    "ORANGE"                   : {"faces":{"all": "orange"           }},
    "HELLORANGE"               : {"faces":{"all": "hellorange"       }},
    "HELLBLAU"                 : {"faces":{"all": "hellblau"         }},
    "HELLGRAU"                 : {"faces":{"all": "hellgrau"         }},
    "WEISS"                    : {"faces":{"all": "weiss"            }},
    "MITTELDUNKELLILA"         : {"faces":{"all": "mitteldunkellila" }},
    "DUNKELLILA"               : {"faces":{"all": "dunkellila"       }},
    "GRAU-BRAUN"               : {"faces":{"all": "grau-braun"       }},
    "MITTELGRAU"               : {"faces":{"all": "mittelgrau"       }},
    "OLIVE"                    : {"faces":{"all": "olive"            }},
    "DUNKELBLAU"               : {"faces":{"all": "dunkelblau"       }},
    "SILBER"                   : {"faces":{"all": "silber"           }},
    "SEMISOLITUDE"             : {"faces":{"all": "semisolitude"     }},
    "DUPLEXFLAVE"              : {"faces":{"all": "duplexflave"      }},
    "PETROL"                   : {"faces":{"all": "petrol"           }},
    "BLAU"                     : {"faces":{"all": "blau"             }},
    "HELLSCHWARZ"              : {"faces":{"all": "hellschwarz"      }},
    "HELLBRAUN"                : {"faces":{"all": "hellbraun"        }},
    "DUPLEXGRISIO"             : {"faces":{"all": "duplexgriseo"     }},

    # ERZE
    "DIAMANT"                  : {"faces":{"all": "diamant_block"  }},
    "DIAMANTERZ"               : {"faces":{"all": "diamant_erz"    }},
    "GOLD"                     : {"faces":{"all": "gold_block"     }},
    "GOLDERZ"                  : {"faces":{"all": "gold_erz"       }},
    "NETHERGOLD"               : {"faces":{"all": "nether_gold_erz"}},
    "IRON"                     : {"faces":{"all": "eisen_block"    }}, # umbenennen zu EISEN?
    "EISENERZ"                 : {"faces":{"all": "eisen_erz"      }},
    #"KOHLE"                    : {"faces":{"all": "kohle_block"    }},
    "KOHLEERZ"                 : {"faces":{"all": "kohle_erz"      }},
    "REDSTONE"                 : {"faces":{"all": "redstone_block" }},
    "Redstone"                 : {"faces":{"all": "redstone_block" }}, # entfernen?
    #"REDSTONEERZ"              : {"faces":{"all": "redstone_erz"   }},
    "SMARAGTBLOCK"             : {"faces":{"all": "smaragd_block"  }}, # umbenennen zu SMARAGD?
    "SMARAGTERZ"               : {"faces":{"all": "smaragd_erz"    }}, # umbenennen zu SMARAGDERZ?
    "LAPIS"                    : {"faces":{"all": "lapis_block"    }},
    "Lapiserz"                 : {"faces":{"all": "lapis_erz"      }}, #umbenennen zu LAPISERZ?

    # Gesichter
    "GESICHT"                  : {"icon":"gesicht_front",            "faces":{"top":"gesicht_top",         "bottom":"gesicht_bottom",      "front":"gesicht_front",             "back":"gesicht_back",      "left":"gesicht_left",      "right":"gesicht_right"     }},
    "GESICHT_SMILE"            : {"icon":"gesicht_front_smile",      "faces":{"top":"gesicht_top",         "bottom":"gesicht_bottom",      "front":"gesicht_front_smile",       "back":"gesicht_back",      "left":"gesicht_left",      "right":"gesicht_right"     }},
    "GESICHT_HOLLOW_EYES"      : {"icon":"gesicht_front_hollow_eyes","faces":{"top":"gesicht_top",         "bottom":"gesicht_bottom",      "front":"gesicht_front_hollow_eyes", "back":"gesicht_back",      "left":"gesicht_left",      "right":"gesicht_right"     }},
    "Damengesicht"             : {"icon":"damengesicht_front", "faces":{"top":"damengesicht_bottom", "bottom":"damengesicht_bottom", "front":"damengesicht_front", "back":"damengesicht_back", "left":"damengesicht_left", "right":"damengesicht_right"}},
    "CREEPER"                  : {"icon":"creeper_face", "faces":{"front":"creeper_face", "other":"creeper"    }},
    "Zombie"                   : {"icon": "zombie_face", "faces":{"front": "zombie_face", "other":"dunkelgrau" }},
    "Skelett"                  : {"icon":"skelett_face", "faces":{"front":"skelett_face", "other":"weiss"      }},
    "Schaf"                    : {"icon":  "schaf_face", "faces":{"front":  "schaf_face", "other":"weiss"      }},
    "Geist"                    : {"icon":  "geist_face", "faces":{"front":  "geist_face", "bottom":"commandblock", "other":"hellblau"}},

    # Beine
    "Schafbeine"               : {"faces":{"top":"weiss",       "bottom":"schwarz",        "other":"schafbeine"    }},
    "Menschenbeine"            : {"faces":{"top":"gesicht_top", "bottom":"gesicht_bottom", "other":"menschenbeine" }},
    "Damenbeine"               : {"faces":{"top":"hellgrau",    "bottom":"rot",            "other":"damenbeine"    }},
    "HAUT"                     : {"faces":{"all":"HAUT"}},
    #Oberkoerper
    "Damenkoerper"             : {"faces":{"all":"damenkoerper"}},

    # REDSTONE
    "Commandblock"             : {"faces":{"all":"commandblock"}},
    "LAMPOFF"                  : {"icon":None, "faces":{"all":"lamp_off"}},
    "LAMPON"                   : {"icon":None, "faces":{"all":"lamp_on"}},
    "FAN"                      : {"faces":{"top":"fan", "other":"reinforced_stone"}},
    "Repeater"                 : {"faces":{"bottom":"repeater_off", "other":"transparent"}, "icon":"repeater_off", "transparent":True},
    "Piston"                   : {"faces":{"top":"piston_top","bottom":"piston_bottom","other":"piston_side"}, "icon":"piston_side"},
    "Noteblock"                : {"faces":{"all":"noteblock"}},

    # EXPLOSIV
    "RACKETENWERFER"           : {"faces":{"back":"racketenwerfer_back","left":"racketenwerfer_side","right":"racketenwerfer_side","other":"racketenwerfer_front"}},
    "TNT"                      : {"faces":{"top":"tnt_top", "bottom": "tnt_bottom", "other": "tnt_side" }},
    "A-TNT"                    : {"faces":{"top":"atnt_top","bottom": "atnt_bottom","other": "atnt_side"}},
    "B-TNT"                    : {"faces":{"top":"btnt_top","bottom": "btnt_bottom","other": "btnt_side"}},

    "Fruhlingsgrass"           : {"faces":{"top":"fruhlingsgrass_top", "bottom":"dirt",    "other":"grass_side" }},
    "Fruhlingslaub"            : {"faces":{"all":"fruhlingslaub"}},
    
    "Quarzsaule"               : {"faces":{"top":"quarzsaule_querschnitt","bottom":"quarzsaule_querschnitt","other":"quarzsaule"}},
    "GLAS"                     : {"faces":{"all":"glas"}, "transparent":True, "connecting":True},
    "Netherstone"              : {"faces":{"all":"netherstone"}},
    "Bucherregal"              : {"faces":{"top":"holzbretter","bottom":"holzbretter","other":"bucherregal"}, "icon":"bucherregal"},
    "Obsidian"                 : {"faces":{"all":"obsidian"}},
    "Prismarin"                : {"faces":{"all":"prismarin"}},
    "Rissige_Steinziegel"      : {"faces":{"all":"rissige_steinziegel"}},
    "Steinziegel"              : {"faces":{"all":"steinziegel"}},
    "STEINZIEGEL"              : {"faces":{"all":"steinstufe_surface"}},
    "Gemeisselter_Steinziegel" : {"faces":{"all":"gemeisselter_steinziegel"}},
    "CHEST"                    : {"faces":{"top":"chest_top","bottom":"chest_bottom","front":"chest_front","other":"chest_side"}, "icon":"chest_front"},
    "DOORTOP"                  : {"icon":None, "faces":{"top":"door_closed_surface","bottom":"door_closed_surface", "other":"door_closed_upper_half"}},
    "DOORBOTTOM"               : {"icon":None, "faces":{"top":"door_closed_surface","bottom":"door_closed_surface", "other":"door_closed_lower_half"}},
    "DOORTOPOPEN"              : {"icon":None, "faces":{"top":"door_open_surface",  "bottom":"transparent",   "other":"door_open_upper_half"}, "transparent":True},
    "DOORBOTTOMOPEN"           : {"icon":None, "faces":{"top":"transparent",  "bottom":"door_open_surface",   "other":"door_open_lower_half"}, "transparent":True},
    "PORTAL"                   : {"faces":{"all":"portal"}},
    "BARRIER"                  : {"faces":{"all":"transparent"}, "transparent":True},
    "WAND"                     : {"faces":{"all":"grun"}},
    "AIM"                      : {"faces":{"all":"gold"}},
    "KAKTUS"                   : {"faces":{"bottom":"kaktus_querschnitt","other":"kaktus_side"}},

    "WATER"                    : {"faces":{"all":"water_surface"}, "transparent":True, "fog_color":(136,170,255,80), "connecting":True},
    },

"ITEMS" : {
    # Items for Blocks will be created automatically

    "Muenzen"                  : {"icon":"muenze"                },
    "Scheine"                  : {"icon":"schein"                },
    "Kredidtkarte"             : {"icon":"kredidtkarte"          },
    "ARROW"                    : {"icon":"ARROW"                 },
    "TORCH"                    : {"icon":"torch_red"             },
    "LAMP"                     : {"icon":"lamp_off"              },
    "HERZ"                     : {"icon":"herz"                  },
    "DOOR"                     : {"icon":"door"                  },
    "Fertilizer"               : {"icon":"fairy_dust"            },
    "Stick1"                   : {"icon":"stick1"                },
    "Stick2"                   : {"icon":"stick2"                },
    "Stick3"                   : {"icon":"stick3"                },
    "Bow"                      : {"icon":"bow"                   },
    "Axe"                      : {"icon":"axe"                   },
    "Fishing_Rod"              : {"icon":"fishing_rod"           },
    "InstaPick"                : {"icon":"instapick"             },
    "InfiniPick"               : {"icon":"infinipick"            },
    "String"                   : {"icon":"string"                },
    "Glue"                     : {"icon":"glue"                  },
    "Saddle"                   : {"icon":"saddle"                },
    "inventory_background"     : {"icon":"inventory_background"  },
    "inventory_border_right"   : {"icon":"inventory_border_blue" },
    "inventory_border_left"    : {"icon":"inventory_border_red"  },
    "inventory_border_mixed"   : {"icon":"inventory_border_red_blue"},
    },

#"ICONS" : {
#    "ARROW"                    : "ARROW",
#    "inventory_background"     : "inventory_background",
#    "inventory_border_right"   : "inventory_border_blue",
#    "inventory_border_left"    : "inventory_border_red",
#    "inventory_border_mixed"   : "inventory_border_red_blue",
#}

#{
#   "NAME" : {
#       "icon" : "missing_texture",
#       "transparent" : True,
#       "faces" : {
#           "top"    : [],
#           "bottom" : [],
#           "front"  : [],
#           "back"   : [],
#           "left"   : [],
#           "right"  : [],
#           "inside" : [],
#       }
#   }
#}

"BLOCK_MODELS": {
    "Setzling"    : {"icon" : "setzling",       "faces" : {"inside": [(((0,0,0),(1,0,1),(1,1,1),(0,1,0)),"setzling"),
                                                                      (((0,0,1),(1,0,0),(1,1,0),(0,1,1)),"setzling")]}},
    "grass"       : {"icon" : "grass",          "faces" : {"inside": [(((0,0,0),(1,0,1),(1,1,1),(0,1,0)),"grass"),
                                                                      (((0,0,1),(1,0,0),(1,1,0),(0,1,1)),"grass")]}},
    "WeisseBlume" : {"icon" : "weisse_blume",   "faces" : {"inside": [(((0,0,0),(1,0,1),(1,1,1),(0,1,0)),"weisse_blume"),
                                                                      (((0,0,1),(1,0,0),(1,1,0),(0,1,1)),"weisse_blume")]}},
    "LilaBlume"   : {"icon" : "lila_blume",     "faces" : {"inside": [(((0,0,0),(1,0,1),(1,1,1),(0,1,0)),"lila_blume"),
                                                                      (((0,0,1),(1,0,0),(1,1,0),(0,1,1)),"lila_blume")]}},
    "RoteBlume"   : {"icon" : "rote_blume",     "faces" : {"inside": [(((0,0,0),(1,0,1),(1,1,1),(0,1,0)),"rote_blume"),
                                                                      (((0,0,1),(1,0,0),(1,1,0),(0,1,1)),"rote_blume")]}},
    "GelbeBlume"  : {"icon" : "gelbe_blume",    "faces" : {"inside": [(((0,0,0),(1,0,1),(1,1,1),(0,1,0)),"gelbe_blume"),
                                                                      (((0,0,1),(1,0,0),(1,1,0),(0,1,1)),"gelbe_blume")]}},
    "SonnenBlume" : {"icon" : "sonnenblume",    "faces" : {"inside": [(((0,0,0),(1,0,1),(1,1,1),(0,1,0)),"sonnenblume"),
                                                                      (((0,0,1),(1,0,0),(1,1,0),(0,1,1)),"sonnenblume")]}},
    "BlaueBlume"  : {"icon" : "blaue_blume",    "faces" : {"inside": [(((0,0,0),(1,0,1),(1,1,1),(0,1,0)),"blaue_blume"),
                                                                      (((0,0,1),(1,0,0),(1,1,0),(0,1,1)),"blaue_blume")]}},
    "HALM"        : {"icon" : "HALM",           "faces" : {"inside": [(((0,0,0),(1,0,1),(1,1,1),(0,1,0)),"HALM"),
                                                                      (((0,0,1),(1,0,0),(1,1,0),(0,1,1)),"HALM")]}},
    "GLAS"        : {"icon" : "glas",           "faces" : {"top"   : [(((0,1,1),(1,1,1),(1,1,0),(0,1,0)),"glas")],
                                                           "bottom": [(((1,0,1),(0,0,1),(0,0,0),(1,0,0)),"glas")],
                                                           "front" : [(((0,0,1),(1,0,1),(1,1,1),(0,1,1)),"glas")],
                                                           "back"  : [(((1,0,0),(0,0,0),(0,1,0),(1,1,0)),"glas")],
                                                           "left"  : [(((0,0,0),(0,0,1),(0,1,1),(0,1,0)),"glas")],
                                                           "right" : [(((1,0,1),(1,0,0),(1,1,0),(1,1,1)),"glas")]},
                     "connecting":True},
    "WATER"       : {"icon" : "many_water",     "faces" : {"top"   : [(((0,1,1),(1,1,1),(1,1,0),(0,1,0)),"water_surface")], #many_water
                                                           "bottom": [(((1,0,1),(0,0,1),(0,0,0),(1,0,0)),"not_many_water")],
                                                           "front" : [(((0,0,1),(1,0,1),(1,1,1),(0,1,1)),"not_many_water")],
                                                           "back"  : [(((1,0,0),(0,0,0),(0,1,0),(1,1,0)),"not_many_water")],
                                                           "left"  : [(((0,0,0),(0,0,1),(0,1,1),(0,1,0)),"not_many_water")],
                                                           "right" : [(((1,0,1),(1,0,0),(1,1,0),(1,1,1)),"not_many_water")]},
                     "fog_color":(136,170,255,80), "connecting":True},
    "HEBEL"       : {"icon" : "hebel",          "faces" : {"front" : [((    (1,0,1),    (0,0,1),(  0,0.5,1),  (1,0.5,1)),("doppelsteinstufe", 0,0,1, 0.5))],
                                                           "back"  : [((    (0,0,0),    (1,0,0),(  1,0.5,0),  (0,0.5,0)),("doppelsteinstufe", 0,0,1, 0.5))],
                                                           "left"  : [((    (0,0,1),    (0,0,0),(  0,0.5,0),  (0,0.5,1)),("doppelsteinstufe", 0,0,1, 0.5))],
                                                           "right" : [((    (1,0,0),    (1,0,1),(  1,0.5,1),  (1,0.5,0)),("doppelsteinstufe", 0,0,1, 0.5))],
                                                           "inside": [((  (0,0.5,0),  (1,0.5,0),(  1,0.5,1),  (0,0.5,1)), "steinstufe_surface"           ),
                                                                      (((0.375,0,1),(0.375,1,0),(0.625,1,0),(0.625,0,1)),("holzrinde",        0,0,1,0.25))]}},
    "STONESLAB"   : {"icon" :"doppelsteinstufe","faces" : {"front" : [((    (1,0,1),    (0,0,1),(  0,0.5,1),  (1,0.5,1)),("doppelsteinstufe", 0,0,1, 0.5))],
                                                           "back"  : [((    (0,0,0),    (1,0,0),(  1,0.5,0),  (0,0.5,0)),("doppelsteinstufe", 0,0,1, 0.5))],
                                                           "left"  : [((    (0,0,1),    (0,0,0),(  0,0.5,0),  (0,0.5,1)),("doppelsteinstufe", 0,0,1, 0.5))],
                                                           "right" : [((    (1,0,0),    (1,0,1),(  1,0.5,1),  (1,0.5,0)),("doppelsteinstufe", 0,0,1, 0.5))],
                                                           "bottom": [((    (0,0,0),    (1,0,0),(  1,  0,1),  (0,  0,1)), "steinstufe_surface"           )],
                                                           "inside": [((  (0,0.5,0),  (1,0.5,0),(  1,0.5,1),  (0,0.5,1)), "steinstufe_surface"           )]}},
    "TORCHRED"    : {"icon" : None,             "faces" : {"inside": [(((0,0,0.5), (1,0,0.5), (1,1,0.5), (0,1,0.5)), "torch_red"),
                                                                      (((0.5,0,0), (0.5,0,1), (0.5,1,1), (0.5,1,0)), "torch_red")]}},
    "TORCHBLUE"   : {"icon" : None,             "faces" : {"inside": [(((0,0,0.5), (1,0,0.5), (1,1,0.5), (0,1,0.5)), "torch_blue"),
                                                                      (((0.5,0,0), (0.5,0,1), (0.5,1,1), (0.5,1,0)), "torch_blue")]}},
    "TORCHOFF"    : {"icon" : None,             "faces" : {"inside": [(((0,0,0.5), (1,0,0.5), (1,1,0.5), (0,1,0.5)), "torch_off"),
                                                                      (((0.5,0,0), (0.5,0,1), (0.5,1,1), (0.5,1,0)), "torch_off")]}},
    "ROCKET"      : {"icon" : "rocket",         "faces" : {"inside": [(((0.5,0,0), (0.5,0,1), (0.5,1,1), (0.5,1,0)), "rocket"),
                                                                      (((1,0.5,0), (1,0.5,1), (0,0.5,1), (0,0.5,0)), "rocket")]}},
    "Arrow"       : {"icon" : "arrow_icon",     "faces" : {"inside": [(((0.5,0,0), (0.5,0,1), (0.5,1,1), (0.5,1,0)), "arrow"),
                                                                      (((1,0.5,0), (1,0.5,1), (0,0.5,1), (0,0.5,0)), "arrow")]}},

    "Redstone0"   : {"icon" : None, "faces" : {"inside": [(((0.375, 0.1, 0), (0.625, 0.1, 0), (0.625, 0.1, 1), (0.375, 0.1, 1)),("redstone_dust_0" , 0.0 , 0, 0.25, 1)),    (((1, 0.1, 0.375), (1, 0.1, 0.625), (0, 0.1, 0.625), (0, 0.1, 0.375)), ("redstone_dust_0" , 0.0 , 0, 0.25, 1))]}},
    "Redstone1"   : {"icon" : None, "faces" : {"inside": [(((0.375, 0.1, 0), (0.625, 0.1, 0), (0.625, 0.1, 1), (0.375, 0.1, 1)),("redstone_dust_0" , 0.25, 0, 0.25, 1)),    (((1, 0.1, 0.375), (1, 0.1, 0.625), (0, 0.1, 0.625), (0, 0.1, 0.375)), ("redstone_dust_0" , 0.25, 0, 0.25, 1))]}},
    "Redstone2"   : {"icon" : None, "faces" : {"inside": [(((0.375, 0.1, 0), (0.625, 0.1, 0), (0.625, 0.1, 1), (0.375, 0.1, 1)),("redstone_dust_0" , 0.5 , 0, 0.25, 1)),    (((1, 0.1, 0.375), (1, 0.1, 0.625), (0, 0.1, 0.625), (0, 0.1, 0.375)), ("redstone_dust_0" , 0.5 , 0, 0.25, 1))]}},
    "Redstone3"   : {"icon" : None, "faces" : {"inside": [(((0.375, 0.1, 0), (0.625, 0.1, 0), (0.625, 0.1, 1), (0.375, 0.1, 1)),("redstone_dust_0" , 0.75, 0, 0.25, 1)),    (((1, 0.1, 0.375), (1, 0.1, 0.625), (0, 0.1, 0.625), (0, 0.1, 0.375)), ("redstone_dust_0" , 0.75, 0, 0.25, 1))]}},
    "Redstone4"   : {"icon" : None, "faces" : {"inside": [(((0.375, 0.1, 0), (0.625, 0.1, 0), (0.625, 0.1, 1), (0.375, 0.1, 1)),("redstone_dust_4" , 0.0 , 0, 0.25, 1)),    (((1, 0.1, 0.375), (1, 0.1, 0.625), (0, 0.1, 0.625), (0, 0.1, 0.375)), ("redstone_dust_4" , 0.0 , 0, 0.25, 1))]}},
    "Redstone5"   : {"icon" : None, "faces" : {"inside": [(((0.375, 0.1, 0), (0.625, 0.1, 0), (0.625, 0.1, 1), (0.375, 0.1, 1)),("redstone_dust_4" , 0.25, 0, 0.25, 1)),    (((1, 0.1, 0.375), (1, 0.1, 0.625), (0, 0.1, 0.625), (0, 0.1, 0.375)), ("redstone_dust_4" , 0.25, 0, 0.25, 1))]}},
    "Redstone6"   : {"icon" : None, "faces" : {"inside": [(((0.375, 0.1, 0), (0.625, 0.1, 0), (0.625, 0.1, 1), (0.375, 0.1, 1)),("redstone_dust_4" , 0.5 , 0, 0.25, 1)),    (((1, 0.1, 0.375), (1, 0.1, 0.625), (0, 0.1, 0.625), (0, 0.1, 0.375)), ("redstone_dust_4" , 0.5 , 0, 0.25, 1))]}},
    "Redstone7"   : {"icon" : None, "faces" : {"inside": [(((0.375, 0.1, 0), (0.625, 0.1, 0), (0.625, 0.1, 1), (0.375, 0.1, 1)),("redstone_dust_4" , 0.75, 0, 0.25, 1)),    (((1, 0.1, 0.375), (1, 0.1, 0.625), (0, 0.1, 0.625), (0, 0.1, 0.375)), ("redstone_dust_4" , 0.75, 0, 0.25, 1))]}},
    "Redstone8"   : {"icon" : None, "faces" : {"inside": [(((0.375, 0.1, 0), (0.625, 0.1, 0), (0.625, 0.1, 1), (0.375, 0.1, 1)),("redstone_dust_8" , 0.0 , 0, 0.25, 1)),    (((1, 0.1, 0.375), (1, 0.1, 0.625), (0, 0.1, 0.625), (0, 0.1, 0.375)), ("redstone_dust_8" , 0.0 , 0, 0.25, 1))]}},
    "Redstone9"   : {"icon" : None, "faces" : {"inside": [(((0.375, 0.1, 0), (0.625, 0.1, 0), (0.625, 0.1, 1), (0.375, 0.1, 1)),("redstone_dust_8" , 0.25, 0, 0.25, 1)),    (((1, 0.1, 0.375), (1, 0.1, 0.625), (0, 0.1, 0.625), (0, 0.1, 0.375)), ("redstone_dust_8" , 0.25, 0, 0.25, 1))]}},
    "Redstone10"  : {"icon" : None, "faces" : {"inside": [(((0.375, 0.1, 0), (0.625, 0.1, 0), (0.625, 0.1, 1), (0.375, 0.1, 1)),("redstone_dust_8" , 0.5 , 0, 0.25, 1)),    (((1, 0.1, 0.375), (1, 0.1, 0.625), (0, 0.1, 0.625), (0, 0.1, 0.375)), ("redstone_dust_8" , 0.5 , 0, 0.25, 1))]}},
    "Redstone11"  : {"icon" : None, "faces" : {"inside": [(((0.375, 0.1, 0), (0.625, 0.1, 0), (0.625, 0.1, 1), (0.375, 0.1, 1)),("redstone_dust_8" , 0.75, 0, 0.25, 1)),    (((1, 0.1, 0.375), (1, 0.1, 0.625), (0, 0.1, 0.625), (0, 0.1, 0.375)), ("redstone_dust_8" , 0.75, 0, 0.25, 1))]}},
    "Redstone12"  : {"icon" : None, "faces" : {"inside": [(((0.375, 0.1, 0), (0.625, 0.1, 0), (0.625, 0.1, 1), (0.375, 0.1, 1)),("redstone_dust_12", 0.0 , 0, 0.25, 1)),    (((1, 0.1, 0.375), (1, 0.1, 0.625), (0, 0.1, 0.625), (0, 0.1, 0.375)), ("redstone_dust_12", 0.0 , 0, 0.25, 1))]}},
    "Redstone13"  : {"icon" : None, "faces" : {"inside": [(((0.375, 0.1, 0), (0.625, 0.1, 0), (0.625, 0.1, 1), (0.375, 0.1, 1)),("redstone_dust_12", 0.25, 0, 0.25, 1)),    (((1, 0.1, 0.375), (1, 0.1, 0.625), (0, 0.1, 0.625), (0, 0.1, 0.375)), ("redstone_dust_12", 0.25, 0, 0.25, 1))]}},
    "Redstone14"  : {"icon" : None, "faces" : {"inside": [(((0.375, 0.1, 0), (0.625, 0.1, 0), (0.625, 0.1, 1), (0.375, 0.1, 1)),("redstone_dust_12", 0.5 , 0, 0.25, 1)),    (((1, 0.1, 0.375), (1, 0.1, 0.625), (0, 0.1, 0.625), (0, 0.1, 0.375)), ("redstone_dust_12", 0.5 , 0, 0.25, 1))]}},
    "Redstone15"  : {"icon" : None, "faces" : {"inside": [(((0.375, 0.1, 0), (0.625, 0.1, 0), (0.625, 0.1, 1), (0.375, 0.1, 1)),("redstone_dust_12", 0.75, 0, 0.25, 1)),    (((1, 0.1, 0.375), (1, 0.1, 0.625), (0, 0.1, 0.625), (0, 0.1, 0.375)), ("redstone_dust_12", 0.75, 0, 0.25, 1))]}},
    "Redstone-0"   : {"icon" : None, "faces" : {"inside": [(((0.375, 0.1, 0), (0.625, 0.1, 0), (0.625, 0.1, 1), (0.375, 0.1, 1)),("bluestone_dust_0" , 0.0 , 0, 0.25, 1)),    (((1, 0.1, 0.375), (1, 0.1, 0.625), (0, 0.1, 0.625), (0, 0.1, 0.375)), ("bluestone_dust_0" , 0.0 , 0, 0.25, 1))]}},
    "Redstone-1"   : {"icon" : None, "faces" : {"inside": [(((0.375, 0.1, 0), (0.625, 0.1, 0), (0.625, 0.1, 1), (0.375, 0.1, 1)),("bluestone_dust_0" , 0.25, 0, 0.25, 1)),    (((1, 0.1, 0.375), (1, 0.1, 0.625), (0, 0.1, 0.625), (0, 0.1, 0.375)), ("bluestone_dust_0" , 0.25, 0, 0.25, 1))]}},
    "Redstone-2"   : {"icon" : None, "faces" : {"inside": [(((0.375, 0.1, 0), (0.625, 0.1, 0), (0.625, 0.1, 1), (0.375, 0.1, 1)),("bluestone_dust_0" , 0.5 , 0, 0.25, 1)),    (((1, 0.1, 0.375), (1, 0.1, 0.625), (0, 0.1, 0.625), (0, 0.1, 0.375)), ("bluestone_dust_0" , 0.5 , 0, 0.25, 1))]}},
    "Redstone-3"   : {"icon" : None, "faces" : {"inside": [(((0.375, 0.1, 0), (0.625, 0.1, 0), (0.625, 0.1, 1), (0.375, 0.1, 1)),("bluestone_dust_0" , 0.75, 0, 0.25, 1)),    (((1, 0.1, 0.375), (1, 0.1, 0.625), (0, 0.1, 0.625), (0, 0.1, 0.375)), ("bluestone_dust_0" , 0.75, 0, 0.25, 1))]}},
    "Redstone-4"   : {"icon" : None, "faces" : {"inside": [(((0.375, 0.1, 0), (0.625, 0.1, 0), (0.625, 0.1, 1), (0.375, 0.1, 1)),("bluestone_dust_4" , 0.0 , 0, 0.25, 1)),    (((1, 0.1, 0.375), (1, 0.1, 0.625), (0, 0.1, 0.625), (0, 0.1, 0.375)), ("bluestone_dust_4" , 0.0 , 0, 0.25, 1))]}},
    "Redstone-5"   : {"icon" : None, "faces" : {"inside": [(((0.375, 0.1, 0), (0.625, 0.1, 0), (0.625, 0.1, 1), (0.375, 0.1, 1)),("bluestone_dust_4" , 0.25, 0, 0.25, 1)),    (((1, 0.1, 0.375), (1, 0.1, 0.625), (0, 0.1, 0.625), (0, 0.1, 0.375)), ("bluestone_dust_4" , 0.25, 0, 0.25, 1))]}},
    "Redstone-6"   : {"icon" : None, "faces" : {"inside": [(((0.375, 0.1, 0), (0.625, 0.1, 0), (0.625, 0.1, 1), (0.375, 0.1, 1)),("bluestone_dust_4" , 0.5 , 0, 0.25, 1)),    (((1, 0.1, 0.375), (1, 0.1, 0.625), (0, 0.1, 0.625), (0, 0.1, 0.375)), ("bluestone_dust_4" , 0.5 , 0, 0.25, 1))]}},
    "Redstone-7"   : {"icon" : None, "faces" : {"inside": [(((0.375, 0.1, 0), (0.625, 0.1, 0), (0.625, 0.1, 1), (0.375, 0.1, 1)),("bluestone_dust_4" , 0.75, 0, 0.25, 1)),    (((1, 0.1, 0.375), (1, 0.1, 0.625), (0, 0.1, 0.625), (0, 0.1, 0.375)), ("bluestone_dust_4" , 0.75, 0, 0.25, 1))]}},
    "Redstone-8"   : {"icon" : None, "faces" : {"inside": [(((0.375, 0.1, 0), (0.625, 0.1, 0), (0.625, 0.1, 1), (0.375, 0.1, 1)),("bluestone_dust_8" , 0.0 , 0, 0.25, 1)),    (((1, 0.1, 0.375), (1, 0.1, 0.625), (0, 0.1, 0.625), (0, 0.1, 0.375)), ("bluestone_dust_8" , 0.0 , 0, 0.25, 1))]}},
    "Redstone-9"   : {"icon" : None, "faces" : {"inside": [(((0.375, 0.1, 0), (0.625, 0.1, 0), (0.625, 0.1, 1), (0.375, 0.1, 1)),("bluestone_dust_8" , 0.25, 0, 0.25, 1)),    (((1, 0.1, 0.375), (1, 0.1, 0.625), (0, 0.1, 0.625), (0, 0.1, 0.375)), ("bluestone_dust_8" , 0.25, 0, 0.25, 1))]}},
    "Redstone-10"  : {"icon" : None, "faces" : {"inside": [(((0.375, 0.1, 0), (0.625, 0.1, 0), (0.625, 0.1, 1), (0.375, 0.1, 1)),("bluestone_dust_8" , 0.5 , 0, 0.25, 1)),    (((1, 0.1, 0.375), (1, 0.1, 0.625), (0, 0.1, 0.625), (0, 0.1, 0.375)), ("bluestone_dust_8" , 0.5 , 0, 0.25, 1))]}},
    "Redstone-11"  : {"icon" : None, "faces" : {"inside": [(((0.375, 0.1, 0), (0.625, 0.1, 0), (0.625, 0.1, 1), (0.375, 0.1, 1)),("bluestone_dust_8" , 0.75, 0, 0.25, 1)),    (((1, 0.1, 0.375), (1, 0.1, 0.625), (0, 0.1, 0.625), (0, 0.1, 0.375)), ("bluestone_dust_8" , 0.75, 0, 0.25, 1))]}},
    "Redstone-12"  : {"icon" : None, "faces" : {"inside": [(((0.375, 0.1, 0), (0.625, 0.1, 0), (0.625, 0.1, 1), (0.375, 0.1, 1)),("bluestone_dust_12", 0.0 , 0, 0.25, 1)),    (((1, 0.1, 0.375), (1, 0.1, 0.625), (0, 0.1, 0.625), (0, 0.1, 0.375)), ("bluestone_dust_12", 0.0 , 0, 0.25, 1))]}},
    "Redstone-13"  : {"icon" : None, "faces" : {"inside": [(((0.375, 0.1, 0), (0.625, 0.1, 0), (0.625, 0.1, 1), (0.375, 0.1, 1)),("bluestone_dust_12", 0.25, 0, 0.25, 1)),    (((1, 0.1, 0.375), (1, 0.1, 0.625), (0, 0.1, 0.625), (0, 0.1, 0.375)), ("bluestone_dust_12", 0.25, 0, 0.25, 1))]}},
    "Redstone-14"  : {"icon" : None, "faces" : {"inside": [(((0.375, 0.1, 0), (0.625, 0.1, 0), (0.625, 0.1, 1), (0.375, 0.1, 1)),("bluestone_dust_12", 0.5 , 0, 0.25, 1)),    (((1, 0.1, 0.375), (1, 0.1, 0.625), (0, 0.1, 0.625), (0, 0.1, 0.375)), ("bluestone_dust_12", 0.5 , 0, 0.25, 1))]}},
    "Redstone-15"  : {"icon" : None, "faces" : {"inside": [(((0.375, 0.1, 0), (0.625, 0.1, 0), (0.625, 0.1, 1), (0.375, 0.1, 1)),("bluestone_dust_12", 0.75, 0, 0.25, 1)),    (((1, 0.1, 0.375), (1, 0.1, 0.625), (0, 0.1, 0.625), (0, 0.1, 0.375)), ("bluestone_dust_12", 0.75, 0, 0.25, 1))]}},
    #["Repeater0On",              True ,        , [[],[],[],[],[],[],[(0,0.1,0,0,0.1,1,1,0.1,1,1,0.1,0),
    },

"ENTITY_MODELS": {
    "MENSCH":{
        "head":[((0,-0.6,0),(0,0.6,0),(1,1,1),"<<head>>")],
        "body":[((0,-0.7,0),(0,0,0),(1,0.4,0.6),"<<body>>")],
        "legl":[],#((0.3,0,0),(0,0,0),(0.4,0.6,0.4),"Menschenbeine")],
        "legr":[],#((-0.3,0,0),(0,0,0),(0.4,0.6,0.4),"Menschenbeine")],
        },
    "ITEM":{
        "head":[],
        "body":[((0,0,0),(0,0,0),(0.4,0.4,0.4),"<<item>>")],
        "legl":[],
        "legr":[],
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
    "SCHAF,GESCHOREN":{
        "head":[((0,0,0),(0,0.8,-0.75),(0.7,0.7,0.6),"Schaf:2")],
        "body":[((0,0,0),(0,0,0),(1.1,1.1,1.7),"HAUT")],
        "legl":[((0.35,-0.3,0.55),(0,-0.5,0),(0.35,1,0.35),"HAUT"),
                ((0.35,-0.3,-0.55),(0,-0.5,0),(0.35,1,0.35),"HAUT")],
        "legr":[((-0.35,-0.3,-0.55),(0,-0.5,0),(0.35,1,0.35),"HAUT"),
                ((-0.35,-0.3,0.55),(0,-0.5,0),(0.35,1,0.35),"HAUT")],
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
    "ARROW":{
        "head":[((0,0,0),(0,0,0),(1,1,1),"Arrow")],
        "body":[],
        "legl":[],
        "legr":[],
        },
    },

"SOUNDS":{
    "cat1":"cat1.mp3",
    }

}
