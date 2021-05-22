from counterpoint_module.Counterpoint import *
class FifthSpecies(Counterpoint):
    def __init__(self, cf, ctp_position="above"):
        super(FifthSpecies, self).__init__(cf, ctp_position)
        self.species = "fifth"
        self.ERROR_THRESHOLD = 100
        self.MAX_SEARCH_WIDTH = 3
        self.ctp.set_rhythm(self.get_rhythm())
        self.rhythm = self.ctp.melody_rhythm.copy()
        self.num_notes = sum(len(row) for row in self.rhythm)
        self.ctp.set_ties(self.get_ties())
        self.search_domain = self._possible_notes()
        self.ctp.set_melody(self.randomize_ctp_melody())

    """ HELP FUNCTIONS"""

    def get_downbeats(self):
        indices = list(range(len(self.cf.melody)))
        return indices[::2]

    def get_upbeats(self):
        indices = list(range(len(self.cf.melody)))
        return indices[1::2]

    """ RHYTHMIC RULES """

    def get_rhythm(self):
        rhythm = []
        measure_rhythms = [(2,2,2,2),(4,2,2),(2,2,4),(4,4),(2,1,1,2,2),(2,1,1,4),(4,2,1,1),(2,2,2,1,1),(2,1,1,2,2)]
        rhytmic_weights = [100,50,75,25,10,5,5,5,5]
        for measures in range(len(self.cf.melody)-1):
            if measures == 0:
                rhythm.append((4,4))
            else:
                rhythm.append(rm.choices(measure_rhythms,rhytmic_weights)[0])
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
        measure = m
        note_number = n
        add_diss = False
        if self.rhythm[m][n] == 1:
            add_diss = True
        if sum(self.rhythm[m][:n]) in [2,6]:
            add_diss = True
        poss = super(FifthSpecies, self).get_consonant_possibilities(cf_note)
        if add_diss:
            for diss in self.dissonant_intervals:
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
                    poss[i] = self._penultimate_notes(self.cf.melody[-1])
                elif m == len(self.rhythm) - 1:
                    # Last measure
                    poss[i] = self._end_notes()
                else:
                    poss[i] = self.get_harmonic_possibilities(m,n, self.cf.melody[m])
                i += 1
        return poss