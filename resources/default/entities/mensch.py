from resources import *
import time, random

@register_entity("Mensch")

class Mensch(Entity):
    LEGS = ["missing_texture", "TESTBLOCK", "SAND", "SANDSTEIN", "BRICK", "BEDROCK", "DIRT", "STONE", "MOSSSTONE", "HOLZ", "LAUB", "HOLZBRETTER", "GRASS", "Myzeln", "SCHNEEERDE", "BRUCHSTEIN", "SCHNEE", "SCHILDBLOCK", "GELB", "HELLGRUN", "GRUN", "TURKIES", "DUNKELGRUN", "DUNKELGRAU", "LILA", "GRAU", "ROT", "HELLROT", "ROSA", "SCHWARZ", "BRAUN", "ORANGE", "HELLORANGE", "HELLBLAU", "HELLGRAU", "WEISS", "DIAMANT", "DIAMANTERZ", "GOLD", "GOLDERZ", "IRON", "EISENERZ", "KOHLEERZ", "REDSTONE", "Redstone", "SMARAGTBLOCK", "SMARAGTERZ", "LAPIS", "Lapiserz", "GESICHT", "Damengesicht", "CREEPER", "Zombie", "Skelett", "Schaf", "Geist", "Schafbeine", "Menschenbeine", "Damenbeine", "Damenkoerper", "Commandblock", "LAMPOFF", "LAMPON", "FAN", "Repeater", "Piston", "RACKETENWERFER", "TNT", "A-TNT", "B-TNT", "Fruhlingsgrass", "Fruhlingslaub", "Quarzsaule", "GLAS", "Netherstone", "Bucherregal", "Obsidian", "Prismarin", "Rissige_Steinziegel", "Steinziegel", "STEINZIEGEL", "Gemeisselter_Steinziegel", "CHEST", "DOORTOP", "DOORBOTTOM", "DOORTOPOPEN", "DOORBOTTOMOPEN", "DOORSTEP", "BARRIER", "WAND", "AIM", "KAKTUS"]
    EMOTES = ["GESICHT_SMILE:2", "GESICHT_HOLLOW_EYES:2"]

    HITBOX = Hitbox(0.4, 1.8, 1.6)
    LIMIT = 0 # no natural Spawning of Player Characters ;)
    instances = []
    
    def __init__(self, data = None):
        data_defaults = {
            "texture" : "MENSCH",
            "skin" : random.choice(self.LEGS),
            "emote" : self.EMOTES[0],
            "show_emote" : False,
            "SPEED" : 11,
            "FLYSPEED" : 11,
            "JUMPSPEED" : 10,
            "inventory" : [],
            "left_hand" : 0,
            "right_hand" : 1,
            "open_inventory" : False, #set player.entity.foreign_inventory then trigger opening by setting this attribute
            "lives" : 9,
            "tags" : {"random_tick_source","update"},
            "spawn" : (None, None), # (world_index, position)
        }
        if data != None:
            data_defaults.update(data)
        super().__init__(data_defaults)

        self.register_item_callback(self._update_modelmaps,"skin")
        self.register_item_callback(self._update_modelmaps,"emote")
        self.register_item_callback(self._update_modelmaps,"show_emote")


    def _update_modelmaps(self, _):
        modelmaps = {"<<body>>":self["skin"],
                     "<<head>>":"GESICHT:2"}
        if self["show_emote"]:
            modelmaps["<<head>>"] = self["emote"]
        self["modelmaps"] = modelmaps

    def select_emote(self, index):
        self["emote"] = self.EMOTES[index%len(self.EMOTES)]

    def clicked(self, character, item):
        print("Oh no, that hurts!")
        self.take_damage(1)

    def update(self):
        self.execute_ai_commands()

    def take_damage(self, damage):
        self["lives"] -= damage
        if self["lives"] <= 0:
            self.die_and_respawn()

    def die_and_respawn(self):
        # die
        world_index, position = self["spawn"]
        if world_index is None:
            world = self.world.universe.get_spawn_world()
        else:
            world = self.world.universe.worlds[world_index]
        if position is None:
            position = self.world.blocks.world_generator.spawnpoint
        self.set_world(world,position)
        print("respawn", world_index, position)
        # respawn
        self["lives"] = 9
