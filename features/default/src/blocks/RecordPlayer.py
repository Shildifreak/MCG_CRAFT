from resources import *
from rotatable import _RotatableBlock, _RotatableBlockItem


DEFAULT_RECORD_DATA = [
    ("SCHWARZ_block_broken","SCHWARZ_block_placed",), #0
    ("SCHWARZ_block_broken",), #0
    ("DUNKELBLAU_block_broken",), #9
    ("BEIGE_block_broken",), #7
    ("ORANGE_block_broken",), #5
    ("SCHWARZ_block_placed",), #0
    (),
    (),
    ("SCHWARZ_block_broken","SCHWARZ_block_placed",), #0
    ("SCHWARZ_block_broken",), #0
    ("DUNKELBLAU_block_broken",), #9
    ("BEIGE_block_broken",), #7
    ("ORANGE_block_broken",), #5
    ("DUNKELLILA_block_placed",), #2
    (),
    (),
    ("DUNKELLILA_block_broken",), #2
    ("DUNKELLILA_block_broken",), #2
    ("BLAU_block_broken",), #10
    ("DUNKELBLAU_block_broken",), #9
    ("BEIGE_block_broken",), #7
    ("HELLBRAUN_block_placed",), #4
    (),
    (),
    ("HELLGRAU_block_broken",), #12
    ("MITTELGRAU_block_broken",), #14
    ("HELLGRAU_block_broken",), #12
    ("DUNKELBLAU_block_broken",), #9
    ("BEIGE_block_broken","DUNKELLILA_block_broken",), #7
    ("DUNKELBLAU_block_placed","HELLGRUN_block_placed"), #9
    (),
    (),
]

class Record(_RotatableBlockItem):    
    def use_on_air(self, character):
        data = DEFAULT_RECORD_DATA
        for sounds in data:
            for sound in sounds:
                sound_event = Event("sound",Point(character["position"]),sound)
                character.world.event_system.add_event(sound_event)
            yield from wait(0.5)

class Record(_RotatableBlock):
    defaults = Block.defaults.copy()
    defaults["data"] = DEFAULT_RECORD_DATA
    defaults["cursor"] = 0
    defaults["p_ambient"] = True

    def get_break_sounds(self):
        sounds = self["data"][self["cursor"]]
        return sounds

    def handle_event_block_update(self, event):
        r = (self["rotation"] - self["cursor"]) % 4
        match r:
            case 1:
                self["cursor"] += 1
            case 3:
                self["cursor"] -= 1
            case _:
                return False
        self["cursor"] %= len(self["data"])
        self["p_level"] = len(self["data"][self["cursor"]])
        print(self["p_level"])
        return True

    def get_tags(self):
        return super().get_tags() | {"block_update", "sound"}

