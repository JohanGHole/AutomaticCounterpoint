import music_module.music as m
from music_module.constants import *

cf = [60,67,69,67,65,64,62,60]
cf_len = [8,8,8,8,8,8,8,8]

class FirstSpecies:
    def __init__(self,cf_notes,cf_rhythm, key = "C",scaleType = "major",cpt_position = "above", voice = SOPRANO):
        self.key = key
        self.scaleType = scaleType
        self.cpt_position = cpt_position
        self.cf_notes = cf_notes
        self.cf_rhythm = cf_rhythm
        self.voice = voice
        self.scale = m.Scale(key, scaleType, RANGES[voice])
        self.scale = self.scale.get_scale_pitches()
test = FirstSpecies(cf,cf_len)
print(test.scale)
"""
Initialize()
BackTrack()
BestPossibility()

must enforce contrary motion

"""