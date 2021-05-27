from counterpoint_module.Counterpoint import *
class FifthSpecies(Counterpoint):
    def __init__(self, cf, ctp_position="above"):
        super(FifthSpecies, self).__init__(cf, ctp_position)
        self.species = "fifth"
        self.ERROR_THRESHOLD = 100
        self.melody.set_rhythm(self.get_rhythm())
        self.rhythm = self.melody.get_rhythm()
        self.num_notes = sum(len(row) for row in self.rhythm)
        self.melody.set_ties(self.get_ties())
        self.search_domain = self._possible_notes()
        self.melody.set_melody(self.randomize_ctp_melody())

    """ RHYTHMIC RULES """

    def get_rhythm(self):
        rhythm = []
        measure_rhythms = [(2,2,2,2),(4,2,2),(2,2,4),(4,4),
                           (2,1,1,2,2),(2,1,1,4),(4,2,1,1),(2,2,2,1,1),(2,1,1,2,2)]
        rhythmic_weights = [100,50,50,25,10,5,5,5,5]
        for measures in range(len(self.cf.pitches)-1):
            if measures == 0:
                rhythm.append((4,4))
            else:
                rhythm.append(rm.choices(measure_rhythms,rhythmic_weights)[0])
        rhythm.append((8,))
        return rhythm

    def get_ties(self):
        rhythm = self.rhythm
        ties = []
        for m in range(len(rhythm)-1):
            for n in range(len(rhythm[m])):
                if m == 0 and n == 1:
                    ties.append(True)
                elif m > 0 and n == len(rhythm[m])-1:
                    if rhythm[m+1][0] == rhythm[m][n]/2:
                        ties.append(True)
                    else:
                        ties.append(False)
                else:
                    ties.append(False)
        ties.append(False)
        ties.append(False)
        return ties

    """ VOICE INDEPENDENCE RULES """
    """ MELODIC RULES """

    """ HELP FUNCTIONS FOR INITIALIZING COUNTERPOINT"""

    def get_harmonic_possibilities(self, m,n, cf_note):
        add_diss = False
        if self.rhythm[m][n] == 1:
            add_diss = True
        if sum(self.rhythm[m][:n]) in [2,6]:
            add_diss = True
        poss = super(FifthSpecies, self).get_consonant_possibilities(cf_note)
        if add_diss:
            for diss in HARMONIC_DISSONANT_INTERVALS:
                if self.ctp_position == "above":
                    if cf_note + diss in self.scale_pitches:
                        poss.append(cf_note + diss)
                else:
                    if cf_note - diss in self.scale_pitches:
                        poss.append(cf_note - diss)
        return poss

    def _possible_notes(self):
        poss = [None for elem in range(self.num_notes)]
        i = 0
        for m in range(len(self.rhythm)):
            for n in range(len(self.rhythm[m])):
                if m == 0:
                    # First measure. start notes
                    if n == 0:
                        poss[i] = [-1]
                    else:
                        poss[i] = self._start_notes()
                elif m == len(self.rhythm) - 2 and n == len(self.rhythm[m])-1:
                    # penultimate note before last measure.
                    poss[i] = self._penultimate_notes(self.cf.pitches[-1])
                elif m == len(self.rhythm) - 1:
                    # Last measure
                    poss[i] = self._end_notes()
                else:
                    poss[i] = self.get_harmonic_possibilities(m,n, self.cf.pitches[m])
                i += 1
        return poss