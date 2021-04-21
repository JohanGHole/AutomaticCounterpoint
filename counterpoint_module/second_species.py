"""" Second species counterpoint """
from counterpoint_module.first_species import *

class SecondSpecies(FirstSpecies):
    def __init__(self,cf,ctp_position = "above"):
        super(SecondSpecies, self).__init__(cf,ctp_position)
        self.melody_rhythm = [4]*len(self.melody_rhythm)*2
        print(self.melody_rhythm)
        

cf = Cantus_Firmus("C","major",bar_length = 1,voice_range=RANGES[BASS])
cf.generate_cf()
ctp2 = SecondSpecies(cf)
ctp2.construct_ctp_melody(0)
print(ctp2.ctp_melody.melody)
print(ctp2.melody_rhythm)