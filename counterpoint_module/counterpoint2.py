import music_module.music as m
from music_module.constants import *
import math
cf = [60,67,69,67,65,64,62,60]
cf_len = [8,8,8,8,8,8,8,8]
tempo = 120.0


cf = m.Melody(key = "C", scale = "major", bar_length = 1, melody_notes = [60, 67, 69, 67, 65, 64, 62, 60], melody_rhythm = cf_len,voice_range = RANGES[TENOR] )
class Counterpoint:
    melodic_intervals = [Unison, P4,P5,P8,m2,M2,m3,M3,m6]
    harmonic_consonances = [m3,M3,P5,m6,M6,P8,P8+m3,P8+M3]
    def __init__(self,cf,cpt_position = "above", num_voices = 1):
        self.key = cf.key
        self.scale_name = cf.scale_name
        self.cpt_position = cpt_position
        self.cf_notes = cf.melody
        self.cf_rhythm = cf.melody_rhythm
        if cpt_position == "above":
            try:
                self.voice_range = RANGES[RANGES.index(cf.voice_range)+1]
            except:
                print("ERROR. the Cantus Firmus is in the top voice. Writing cpt below instead..")
                self.voice_range = RANGES[RANGES.index(cf.voice_range)-1]
        else:
            try:
                self.voice_range = RANGES[RANGES.index(cf.voice_range)-1]
            except:
                print("ERROR. the Cantus Firmus is in the top voice. Writing cpt below instead..")
                self.voice_range = RANGES[RANGES.index(cf.voice_range)-1]
        self.scale = m.Scale(self.key,self.scale_name, self.voice_range)
        self.scale_pitches = self.scale.get_scale_pitches()
        self.cpt_notes = [None for elem in self.cf_notes]
        print(self.scale_pitches)
    def _initialize(self):
        print("morn du")
test = Counterpoint(cf,cpt_position = "above",num_voices = 1)
print(test.cpt_notes)