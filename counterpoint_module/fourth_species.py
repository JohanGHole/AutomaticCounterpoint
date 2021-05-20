from counterpoint_module.Counterpoint import *
class FourthSpecies(Counterpoint):
    def __init__(self,cf,ctp_position = "above"):
        super(FourthSpecies, self).__init__(cf,ctp_position)
        self.species = "fourth"
        self.ERROR_THRESHOLD = 100
        self.MAX_SEARCH_WIDTH = 3

    """ HELP FUNCTIONS"""

    def get_downbeats(self):
        indices = list(range(len(self.cf_notes)))
        return indices[::2]

    def get_upbeats(self):
        indices = list(range(len(self.cf_notes)))
        return indices[1::2]

    """ RHYTHMIC RULES """

    def get_rhythm(self):
        self.cf_notes = [ele for ele in self.cf_notes for i in range(2)]
        return [4] * len(self.cf_notes)

    def get_harmonic_possibilities(self,i,cf_notes):
        if i in self.get_downbeats():
            poss  = super(FourthSpecies,self).get_consonant_possibilities(cf_notes[i-1])
        else:
            poss = super(FourthSpecies,self).get_consonant_possibilities(cf_notes[i])
        return poss

    def _possible_notes(self):
        poss = [None for elem in self.cf_notes]
        for i in range(len(self.cf_notes)):
            if i == 2 or i == 1 or i == 0:
                poss[i] = self._start_notes()
            elif i == len(self.cf_notes) - 3:
                poss[i] = self._penultimate_notes(self.cf_notes[-1])
            elif i == len(self.cf_notes) - 1 or i == len(self.cf_notes)-2:
                poss[i] = self._end_notes()
            else:
                poss[i] = self.get_harmonic_possibilities(i, self.cf_notes)
        print("possible notes fourth species for ",self.cf_notes,": ",poss)
        return poss
    def post_ornaments(self):
        ctp_draft = []
        ctp_rhythm = [4]
        ctp_draft.append(-1)
        for i in range(1,len(self.ctp_notes)-2):
            if i in self.get_upbeats():
                if self.ctp_notes[i] == self.ctp_notes[i+1]:
                    ctp_draft.append(self.ctp_notes[i])
                    ctp_rhythm.append(8)
                else:
                    ctp_draft.append(self.ctp_notes[i])
                    ctp_rhythm.append(4)
            else:
                if self.ctp_notes[i] != self.ctp_notes[i-1]:
                    ctp_draft.append(self.ctp_notes[i])
                    ctp_rhythm.append(4)
        ctp_draft.append(self.ctp_notes[-1])
        ctp_rhythm.append(8)
        self.ctp_notes = ctp_draft
        self.melody_rhythm = ctp_rhythm

