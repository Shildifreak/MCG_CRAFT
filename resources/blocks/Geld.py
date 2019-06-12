from resources import *
from observableCollections import ObservableDict
# -*- coding: cp1252 -*-
from resources import *
@register_item("Muenzen")
@register_item("Scheine")
class notPlacable(Item):
    def use_on_block(self,character,blockpos,face):
        """whatever this item should do when click on a block... default is to place a block with same id"""
        return self.use_on_air(character)


@register_item("Kredidtkarte")
class Kredidtkarte(notPlacable):
     def use_on_air(self, character):
        # open inventory
        #if not "inventory" in self.item:
        try:
            self.item["inventory"]
        except KeyError:
            self.item["inventory"] = ObservableDict()
            for i in range(28):
                self.item["inventory"][i] = {"id":"AIR"}

        character.foreign_inventory = self.item["inventory"]
        character["open_inventory"] = True
