from counterpoint_module.Counterpoint import *
import math
import search_algorithm.search_algorithm as Search_Algorithm


class FirstSpecies(Counterpoint):
    melodic_intervals = [Unison,m2,M2,m3,M3,P4,P5,P8,-m2,-M2,-m3,-M3,-P4,-P5,-P8]
    dissonant_intervals = [m2,M2,M7,m7,P8+m2,P8+M2]
    harmonic_consonances = [m3,M3,P5,m6,M6,P8,P8+m3,P8+M3]
    perfect_intervals = [P5,P8]
    def __init__(self,cf,ctp_position = "above"):
        super(FirstSpecies,self).__init__(cf,ctp_position)
        self.species = "first"
        self.ERROR_THRESHOLD = 50
        self.MAX_SEARCH_WIDTH = 3

    """ RHYTHM """
    def get_rhythm(self):
        "Voices all move together in the same rhythm as the cantus firmus."
        return [8] * len(self.cf_notes)

    """ HELP FUNCTIONS FOR INITIALIZING COUNTERPOINT"""

    def get_harmonic_possibilities(self,cf_note):
        poss = []
        for interval in self.harmonic_consonances:
            if self.ctp_position == "above":
                if cf_note+interval in self.scale_pitches:
                    poss.append(cf_note+interval)
            else:
                if cf_note-interval in self.scale_pitches:
                    poss.append(cf_note-interval)
        return poss

    def _possible_notes(self):
        poss = [None for elem in self.cf_notes]
        for i in range(len(self.cf_notes)):
            if i == 0:
                poss[i] = self._start_notes()
            elif i == len(self.cf_notes)-2:
                poss[i] = self._penultimate_notes(self.cf_notes[i+1])
            elif i == len(self.cf_notes)-1:
                poss[i] = self._end_notes()
            else:
                poss[i] = self.get_harmonic_possibilities(self.cf_notes[i])
        return poss

    """ INITIALIZING COUNTERPOINT WITH RANDOM VALUES"""

    def _initialize_ctp(self):
        self.melody_rhythm = self.get_rhythm()
        cf_notes = self.cf_notes
        poss = self._possible_notes()
        return cf_notes, poss


    def post_ornaments(self):
        return



