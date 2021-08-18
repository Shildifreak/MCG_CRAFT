from resources import *
import time, random
import json

@register_entity("Mensch")

class Mensch(Entity):
    LEGS = ["missing_texture", "TESTBLOCK", "SAND", "SANDSTEIN", "BRICK", "BEDROCK", "DIRT", "STONE", "MOSSSTONE", "HOLZ", "LAUB", "HOLZBRETTER", "GRASS", "Myzeln", "SCHNEEERDE", "BRUCHSTEIN", "SCHNEE", "SCHILDBLOCK", "GELB", "HELLGRUN", "GRUN", "TURKIES", "DUNKELGRUN", "DUNKELGRAU", "LILA", "GRAU", "ROT", "HELLROT", "ROSA", "SCHWARZ", "BRAUN", "ORANGE", "HELLORANGE", "HELLBLAU", "HELLGRAU", "WEISS", "DIAMANT", "DIAMANTERZ", "GOLD", "GOLDERZ", "IRON", "EISENERZ", "KOHLEERZ", "REDSTONE", "Redstone", "SMARAGTBLOCK", "SMARAGTERZ", "LAPIS", "Lapiserz", "GESICHT", "Damengesicht", "CREEPER", "Zombie", "Skelett", "Schaf", "Geist", "Schafbeine", "Menschenbeine", "Damenbeine", "Damenkoerper", "Commandblock", "LAMPOFF", "LAMPON", "FAN", "Repeater", "Piston", "RACKETENWERFER", "TNT", "A-TNT", "B-TNT", "Fruhlingsgrass", "Fruhlingslaub", "Quarzsaule", "GLAS", "Netherstone", "Bucherregal", "Obsidian", "Prismarin", "Rissige_Steinziegel", "Steinziegel", "STEINZIEGEL", "Gemeisselter_Steinziegel", "CHEST", "DOORTOP", "DOORBOTTOM", "DOORTOPOPEN", "DOORBOTTOMOPEN", "DOORSTEP", "BARRIER", "WAND", "AIM", "KAKTUS"]
    EMOTES = ["GESICHT_SMILE:2", "GESICHT_HOLLOW_EYES:2"]

    HITBOX = Hitbox(0.4, 1.8, 1.6)
    LIMIT = 0 # no natural Spawning of Player Characters ;)
    instances = []
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self["skin"] = random.choice(self.LEGS)
        self["emote"] = self.EMOTES[0]
        self["show_emote"] = False
        self.register_item_callback(self._update_texture,"skin")
        self.register_item_callback(self._update_texture,"emote")
        self.register_item_callback(self._update_texture,"show_emote")

        self["SPEED"] = 11
        self["FLYSPEED"] = 11
        self["JUMPSPEED"] = 10
        self["inventory"] = []
        self["left_hand"] = {"id":"AIR"}
        self["right_hand"] = {"id":"AIR"}
        self["open_inventory"] = False #set player.entity.foreign_inventory then trigger opening by setting this attribute
        self["lives"] = 9
        self["tags"] = {"random_tick_source","update"}

    def _update_texture(self, _):
        texture_mappings = {"<<random>>":self["skin"]}
        if self["show_emote"]:
            texture_mappings["GESICHT:2"] = self["emote"]
        self["texture"] = "MENSCH:%s" % json.dumps(texture_mappings, separators=(',',':'))

    def select_emote(self, index):
        self["emote"] = self.EMOTES[index%len(self.EMOTES)]

    def right_clicked(self, character):
        print("Oh no, that hurts!")
        
    def left_clicked(self, character):
        print("Just stop it already!")

    def update(self):
        self.update_dt()
        self.execute_ai_commands()
