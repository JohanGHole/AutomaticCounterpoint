from counterpoint_module.Counterpoint import *
import math
import search_algorithm.search_algorithm as Search_Algorithm


class FirstSpecies(Counterpoint):
    def __init__(self,cf,ctp_position = "above"):
        super(FirstSpecies,self).__init__(cf,ctp_position)
        self.species = "first"
        self.ERROR_THRESHOLD = 50
        self.melody.set_rhythm(self.get_rhythm())
        self.melody.set_ties(self.get_ties())
        self.search_domain = self._possible_notes()
        self.melody.set_melody(self.randomize_ctp_melody())
    """ RHYTHM """
    def get_rhythm(self):
        "Voices all move together in the same rhythm as the cantus firmus."
        return [(8,)]*self.cf.length

    def get_ties(self):
        return [False]*self.cf.length
    """ HELP FUNCTIONS FOR INITIALIZING COUNTERPOINT"""

    def _possible_notes(self):
        poss = [None for elem in self.melody.rhythm]
        for i in range(len(self.melody.rhythm)):
            if i == 0:
                poss[i] = self._start_notes()
            elif i == len(self.melody.rhythm)-2:
                poss[i] = self._penultimate_notes(self.cf.pitches[i+1])
            elif i == len(self.melody.rhythm)-1:
                poss[i] = self._end_notes()
            else:
                poss[i] = self.get_consonant_possibilities(self.cf.pitches[i])
        return poss



