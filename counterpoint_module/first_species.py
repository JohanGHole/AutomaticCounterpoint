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
        self.MAX_SEARCH_WIDTH = 6
        self.ctp.set_rhythm(self.get_rhythm())
        self.ctp.set_ties(self.get_ties())
        self.search_domain = self._possible_notes()
        self.ctp.set_melody(self.randomize_ctp_melody())
    """ RHYTHM """
    def get_rhythm(self):
        "Voices all move together in the same rhythm as the cantus firmus."
        return [(8,)]*self.cf.length

    def get_ties(self):
        return [False]*len(self.cf.melody)
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
        poss = [None for elem in self.ctp.melody_rhythm]
        for i in range(len(self.ctp.melody_rhythm)):
            if i == 0:
                poss[i] = self._start_notes()
            elif i == len(self.ctp.melody_rhythm)-2:
                poss[i] = self._penultimate_notes(self.cf.melody[i+1])
            elif i == len(self.ctp.melody_rhythm)-1:
                poss[i] = self._end_notes()
            else:
                poss[i] = self.get_harmonic_possibilities(self.cf.melody[i])
        return poss

    """ INITIALIZING COUNTERPOINT WITH RANDOM VALUES"""

    def randomize_ctp_melody(self):
        ctp_melody = []
        i = 0
        measure = 0
        while measure < len(self.ctp.melody_rhythm):
            note_duration = 0
            while note_duration < len(self.ctp.melody_rhythm[measure]):
                if i == 0:
                    ctp_melody.append(rm.choice(self.search_domain[i]))
                if i > 0 and self.ctp.ties[i-1] != True:
                    ctp_melody.append(rm.choice(self.search_domain[i]))
                i += 1
                note_duration += 1
            measure += 1
        return ctp_melody


    def post_ornaments(self):
        return



