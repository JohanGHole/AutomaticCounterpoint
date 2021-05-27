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
        self.ERROR_THRESHOLD = 50
        self.melody.set_rhythm(self.get_rhythm())
        self.num_notes = sum(len(row) for row in self.get_rhythm())
        self.melody.set_ties(self.get_ties())
        self.search_domain = self._possible_notes()
        self.melody.set_melody(self.randomize_ctp_melody())
    """ HELP FUNCTIONS"""
    def get_downbeats(self):
        indices = list(range(len(self.cf.pitches)))*2
        return indices[::2]
    def get_upbeats(self):
        indices = list(range(len(self.cf.pitches)))*2
        return indices[1::2]

    """ RHYTHMIC RULES """
    def get_rhythm(self):
        rhythm = [(4,4)]*(len(self.cf.pitches)-1)
        rhythm.append((8,))
        return rhythm

    def get_ties(self):
        return [False]*self.num_notes

    """ VOICE INDEPENDENCE RULES """
    """ MELODIC RULES """

    """ HELP FUNCTIONS FOR INITIALIZING COUNTERPOINT"""

    def get_harmonic_possibilities(self, idx, cf_note):
        poss = super(SecondSpecies,self).get_consonant_possibilities(cf_note)
        upbeats = self.get_upbeats()
        if idx in upbeats:
            if idx != 1:
                for diss in HARMONIC_DISSONANT_INTERVALS:
                    if self.ctp_position == "above":
                        if cf_note+diss in self.scale_pitches:
                            poss.append(cf_note+diss)
                    else:
                        if cf_note-diss in self.scale_pitches:
                            poss.append(cf_note-diss)
        return poss

    def _possible_notes(self):
        poss = [None for elem in range(self.num_notes)]
        i = 0
        for m in range(len(self.get_rhythm())):
            for n in range(len(self.get_rhythm()[m])):
                if m == 0:
                    # First measure. start notes
                    if n == 0:
                        poss[i] = [-1]
                    else:
                        poss[i] = self._start_notes()
                elif m == len(self.get_rhythm()) - 2 and n == 1:
                    # penultimate note before last measure.
                    poss[i] = self._penultimate_notes(self.cf.pitches[-1])
                elif m == len(self.get_rhythm())-1:
                    # Last measure
                    poss[i] = self._end_notes()
                else:
                    poss[i] = self.get_harmonic_possibilities(i, self.cf.pitches[m])
                i += 1
        return poss