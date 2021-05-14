"""" Second species counterpoint
TODO:
    - Generate a first species counterpoint
    - double the number of notes and split the note length in two
    - for weak beats, check for changes. No need to change the strong-beats since these are already checked
    - End note is a whole note
    - Start may be a rest
    - only dissonance if approached and left by melodic step. Else: consonance


"""
from counterpoint_module.Counterpoint import *

class SecondSpecies(Counterpoint):
    def __init__(self,cf,ctp_position = "above"):
        super(SecondSpecies,self).__init__(cf,ctp_position)
        self.species = "second"
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

    """ VOICE INDEPENDENCE RULES """
    """ MELODIC RULES """

    """ HELP FUNCTIONS FOR INITIALIZING COUNTERPOINT"""

    def get_harmonic_possibilities(self, idx, cf_notes):
        poss = super(SecondSpecies,self).get_consonant_possibilities(cf_notes[idx])
        upbeats = self.get_upbeats()
        if idx in upbeats:
            if idx != 1:
                for diss in self.dissonant_intervals:
                    if self.ctp_position == "above":
                        if cf_notes[idx]+diss in self.scale_pitches:
                            poss.append(cf_notes[idx]+diss)
                    else:
                        if cf_notes[idx]-diss in self.scale_pitches:
                            poss.append(cf_notes[idx]-diss)
        return poss

    def _possible_notes(self):
        poss = [None for elem in self.cf_notes]
        for i in range(len(self.cf_notes)):
            if i == 1 or i == 0:
                poss[i] = self._start_notes()
            elif i == len(self.cf_notes) - 3:
                poss[i] = self._penultimate_notes(self.cf_notes[-1])
            elif i == len(self.cf_notes) - 1 or i == len(self.cf_notes)-2:
                poss[i] = self._end_notes()
            else:
                poss[i] = self.get_harmonic_possibilities(i, self.cf_notes)
        return poss

    """ INITIALIZING COUNTERPOINT WITH RANDOM VALUES"""

    """def _initialize_ctp2(self):
        # Expanding the already generated first species results:
        self.melody_rhythm = self.get_rhythm()
        extended_cf = [ele for ele in self.cf_notes for i in range(2)]
        print("expanded cf_notes: ",extended_cf)
        poss = self._possible_notes2(extended_cf)
        print("poss: ",poss)
        ctp_notes = []
        for p in poss:
            ctp_notes.append(rm.choice(p))
        return ctp_notes.copy(), extended_cf, poss"""

    def post_ornaments(self):
        self.ctp_notes[0] = -1
        self.ctp_notes[-2] = self.ctp_notes[-1]
        self.ctp_notes.pop(-1)
        self.melody_rhythm.pop(-1)
        self.melody_rhythm[-1] = 8


"""cf = Cantus_Firmus("C","major",bar_length = 2)
cf.generate_cf()
ctp = SecondSpecies(cf,ctp_position="above")
ctp.generate_ctp()"""