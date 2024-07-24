from resources import *


class BEDROCK(Block):
    blast_resistance = 1

    def mined(self,character,face):
        """can't mine bedrock, so this function does nothing instead of default something"""
        #print("hey, you can't mine bedrock")

    def get_tags(self):
        return super().get_tags() - {"explosion"} # can't explode
