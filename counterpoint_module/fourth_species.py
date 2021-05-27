from counterpoint_module.Counterpoint import *
class FourthSpecies(Counterpoint):
    def __init__(self, cf, ctp_position="above"):
        super(FourthSpecies, self).__init__(cf, ctp_position)
        self.species = "fourth"
        self.ERROR_THRESHOLD = 25
        self.melody.set_rhythm(self.get_rhythm())
        self.num_notes = sum(len(row) for row in self.get_rhythm())
        self.melody.set_ties(self.get_ties())
        self.search_domain = self._possible_notes()
        self.melody.set_melody(self.randomize_ctp_melody())

    """ HELP FUNCTIONS"""

    """ RHYTHMIC RULES """

    def get_rhythm(self):
        rhythm = [(4, 4)] * (self.cf.length - 1)
        rhythm.append((8,))
        return rhythm

    def get_ties(self):
        ties = []
        for i in range(self.num_notes-2):
            if i%2 == 0:
                ties.append(False)
            else:
                ties.append(True)
        ties.append(False)
        ties.append(False)
        return ties

    """ VOICE INDEPENDENCE RULES """
    """ MELODIC RULES """

    """ HELP FUNCTIONS FOR INITIALIZING COUNTERPOINT"""

    def get_harmonic_possibilities(self, idx, cf_note):
        poss = super(FourthSpecies, self).get_consonant_possibilities(cf_note)
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
                elif m == len(self.get_rhythm()) - 1:
                    # Last measure
                    poss[i] = self._end_notes()
                else:
                    poss[i] = self.get_harmonic_possibilities(i, self.cf.pitches[m])
                i += 1
        return poss

