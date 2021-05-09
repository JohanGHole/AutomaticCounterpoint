"""" Second species counterpoint
TODO:
    - Generate a first species counterpoint
    - double the number of notes and split the note length in two
    - for weak beats, check for changes. No need to change the strong-beats since these are already checked
    - End note is a whole note
    - Start may be a rest
    - only dissonance if approached and left by melodic step. Else: consonance


"""
from counterpoint_module.first_species import *

class SecondSpecies(FirstSpecies):
    def __init__(self,cf,ctp_position = "above"):
        super(SecondSpecies,self).__init__(cf,ctp_position)
        self.ERROR_THRESHOLD = 100
        self.MAX_SEARCH_WIDTH = 3

    """ HELP FUNCTIONS"""
    def get_downbeats(self):
        indices = list(range(len(self.cf_notes)))
        return indices[::2]
    def get_upbeats(self):
        indices = list(range(len(self.cf_notes)))
        return indices[1::2]
    """ MELODIC RULES """

    def _is_motivic_repetitions(self, ctp_draft):
        for i in range(len(ctp_draft) - 3):
            if ctp_draft[i:i + 2] == ctp_draft[i + 2:i + 4]:
                return True
        return False

    def melodic_rules(self, ctp_draft):
        penalty = super(SecondSpecies,self).melodic_rules(ctp_draft)
        if self._is_motivic_repetitions(ctp_draft):
            self.ctp_errors.append("Motivic repetitions!")
            penalty += 25
        return penalty

    """ RHYTHMIC RULES """
    def get_rhythm(self):
        self.cf_notes = [ele for ele in self.cf_notes for i in range(2)]
        return [4] * len(self.cf_notes)

    """ VOICE INDEPENDENCE RULES """

    def _is_parallel_perfects_on_downbeats(self,ctp_draft, upper_voice, lower_voice):
        db = self.get_downbeats()
        for i in range(len(db) - 1):
            interval1 = upper_voice[db[i]] - lower_voice[db[i]]
            interval2 = upper_voice[db[i + 1]] - lower_voice[db[i + 1]]
            if interval1 == interval2 and interval1 in self.perfect_intervals:
                # consecutive perfects on downbeats
                if upper_voice[db[i + 1]] - upper_voice[db[i]] == lower_voice[db[i + 1]] - lower_voice[db[i]]:
                    # consecutive and parallel
                    if ctp_draft[db[i]] - ctp_draft[db[i] + 1] > M3:
                        return False
                    else:
                        return True
                return False
        return False
    def _is_perfect_interval_properly_approached(self,upper_voice,lower_voice,idx):
        if idx == 0 or idx == 1 or idx == len(upper_voice)-2 or idx == len(upper_voice)-1: # the start interval MUST be a perfect interval and is therefore allowed
            return True
        if upper_voice[idx]-lower_voice[idx] in self.perfect_intervals:
            if self.motion(idx,upper_voice,lower_voice) not in ["oblique","contrary"]:
                self.error_idx.append(idx)
                return False
            if self._is_large_leap(upper_voice,idx-1) or self._is_large_leap(lower_voice,idx-1):
                if upper_voice[idx]-lower_voice[idx] == Octave:
                    if self.motion(idx,upper_voice,lower_voice) == "oblique" or idx == len(upper_voice)-1:
                        return True
                else:
                    self.error_idx.append(idx)
                    return False
        return True

    def _is_valid_consecutive_perfect_intervals(self,upper_voice,lower_voice,idx):
        if idx >= len(upper_voice) - 2 or idx == 0:
            return True
        harm_int1 = upper_voice[idx]-lower_voice[idx]
        harm_int2 = upper_voice[idx+1]-lower_voice[idx+1]
        if harm_int1 in self.perfect_intervals and  harm_int2 in self.perfect_intervals:
            if self._is_step(upper_voice,idx) or self._is_step(lower_voice,idx):
                return True
            else:
                return False
                self.error_idx.append(idx)
        return True
    def voice_independence_rules(self, ctp_draft, cf_notes):
        if self.ctp_position == "above":
            upper_voice = ctp_draft
            lower_voice = cf_notes
        else:
            upper_voice = cf_notes
            lower_voice = ctp_draft
        penalty = super(SecondSpecies,self).voice_independence_rules(ctp_draft,cf_notes)
        if self._is_parallel_perfects_on_downbeats(ctp_draft,upper_voice,lower_voice):
            self.ctp_errors.append("Parallel perfect intervals on downbeats!")
            penalty += 100
        return penalty
    """ MELODIC RULES """
    def _is_repeating_pitches(self,ctp_draft):
        total = 0
        if self.ctp_position == "above":
            for i in range(len(ctp_draft)-2): # was 2
                if ctp_draft[i] == ctp_draft[i+1] and i != 0: #== ctp_draft[i+2]:
                    total += 1
        else:
            for i in range(len(ctp_draft) - 2):
                if ctp_draft[i] == ctp_draft[i + 1] and i != 0:
                    total += 1
        return total

    """ DISSONANT RULES"""


    """ HARMONIC RULES """

    """ TOTAL PENALTY"""

    """ HELP FUNCTIONS FOR INITIALIZING COUNTERPOINT"""

    def get_harmonic_possibilities(self, idx, cf_notes):
        poss = super(SecondSpecies,self).get_harmonic_possibilities(cf_notes[idx])
        upbeats = self.get_upbeats()
        if idx in upbeats:
            if idx != 1:
                poss = super(SecondSpecies, self).get_harmonic_possibilities(cf_notes[idx])
                for diss in self.dissonant_intervals:
                    if cf_notes[idx]+diss in self.scale_pitches:
                        poss.append(cf_notes[idx]+diss)
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