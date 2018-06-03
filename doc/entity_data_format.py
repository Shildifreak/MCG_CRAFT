# chunks are in chunk_block_files and are loaded with mmap (write through)
# block entity data (and all other entities) are in chunk_entity_files and loaded with literal_eval into the game
# metadata file in folder that contains stuff like which number is which item -> {1:"mcgcraft:stone",2:"mcgcraft:grass",...}
# block entity files are autosaved in regular intervalls and on exit of the game

world = {
    "chunksize":4,
    "worldgenerator":"colorland",
    "entities" : {"someentity":[0,0,0],"Joram":[0,0,0]},
    # from seperate files:
    "chunks" : {
        (0,0,0) : {
            "block_file" : "bytearray, byte per block depend on number of different blocks inside of this chunk (normally 1)", #loaded with mmap
            "nbt_file" : { #loaded with literal eval
                "entities" : {
                    "someentity" : {
                        "id":"mcgcraft:sheep",
                        "position":(0,0,0),
                        "velocity":(0,0,0),
                        },
                    "Joram" : {
                        "id":"mcgcraft:player",
                        "position":(0,0,0),
                        "velocity":(0,0,0),
                        "password":"schlumpf",
                        "mining":0, #ticks since started mining or last broken block
                        "inventory":[{"id":"minecraft:stuff","count":1,"tags":{}}],
                        "left_hand":{"id":"AIR","count":1},
                        "right_hand":{"id":"GRASS"},
                        "texture":"PLAYER",
                        "hitbox":[(0,0,0)], #list of relative points where collision is tested
                        "health": 10,
                        },
                    },
                "block_entity_data" : {
                    (0,0,0) : {"inventory":[{"id":"mcgcraft:sword","count":4,"slot":5}]}
                    },
                "metadata" : {
                    "byte_per_block":1,
                    "block_codec" : ["mcgcraft:stone","mcgcraft:grass","..."],
                    },
                },
            },
        },
    # runtime
    "active chunks" : [(0,0,0)],
    }

