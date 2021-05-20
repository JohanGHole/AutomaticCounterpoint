from counterpoint_module.Counterpoint import *
class FifthSpecies(Counterpoint):
    def __init__(self,cf,ctp_position = "above"):
        super(FifthSpecies, self).__init__(cf,ctp_position)
        self.species = "fifth"
        self.ERROR_THRESHOLD = 100
        self.MAX_SEARCH_WIDTH = 3

    """ HELP FUNCTIONS"""

    def get_downbeats(self):
        indices = list(range(len(self.cf_notes)))
        return indices[::2]

    def get_upbeats(self):
        indices = list(range(len(self.cf_notes)))
        return indices[1::2]
    def _build_measure(self,i,tied,last_note):
        measure = []
        tied_forward = False
        while sum(measure)
        if i == 0:
            measure.append(4)
            if rm.uniform(0,1) < 0.5:
                measure.append(4)
            else:
                measure.append(4)
                tied_forward = True


    """ RHYTHMIC RULES """
    def _build_measures(self,cf_notes):
        " There are in all 8 time slots for each measure"
        " The passage should not begin with rapid notes"
        " No anapest rhythm (short short long) unless the long note is tied forward"
        " Begin in half rest"
        " If tied, the note tied forward should be half the length. except at final cadence"
        " Max 2 eight notes, and they must always be on beat 2 and 4"
        " if sum = 2 or sum = 6"
        rhythm = [[4,4],[2,2,4],[4,2,2],[2,1,1,2,2],[4,4],[2,1,1,4],[2,1,1,2,2,],[4,4],[4,4],
                  [2,2,4],[4,4],[2,2,2,2],[4,2,1,1],[2,2,4],[2,1,1,2],[8]]
        tied = [None,"forward","backward",None,"forward","both","backward",
                None,"forward","both","both","backward",None,"forward","backward",None]
        return rhythm, tied



    def get_rhythm(self):
        rhythm, tied = self._build_measures(self.cf_notes)


    def get_harmonic_possibilities(self,i,cf_notes):
        if i in self.get_downbeats():
            poss  = super(FifthSpecies,self).get_consonant_possibilities(cf_notes[i-1])
        else:
            poss = super(FifthSpecies,self).get_consonant_possibilities(cf_notes[i])
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