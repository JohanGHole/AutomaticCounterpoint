from counterpoint_module.first_species import *
"""
When the cantus firmus is in the bass:

It is most expressive to create 7-6 and 4-3 suspensions, since these dissonant intervals resolve into imperfect consonances.

9-8 suspensions are less expressive because the dissonant resolves into a bland octave, thus taking away much of its effect.

When the cantus firmus is in the upper voice:

It is most expressive to create 2-3 suspensions, since this is a resolution into a 'sweet' imperfect consonance.

You can also create 4-5 and 7-8 suspensions, but these are less expressive because of the resultion into perfect consonances.
"""
class FourthSpecies(FirstSpecies):
    def __init__(self,cf,ctp_position = "above"):
        super(FourthSpecies, self).__init__(cf,ctp_position)
        self.generate_ctp()
        self.cf = cf
        self.melody_rhythm.insert(0,4)
        self.melody_rhythm[-2] = 4
        self.ctp_notes.insert(0,-1)


cf = Cantus_Firmus("C","major",bar_length =1)
cf.generate_cf()
print("cf rhythm:",cf.melody_rhythm)
print("cf mel: ",cf.melody)
fourths = FourthSpecies(cf)
fourths.construct_ctp_melody(0)
print(fourths.ctp_notes)
print("cf mel after: ",fourths.cf.melody_rhythm)
