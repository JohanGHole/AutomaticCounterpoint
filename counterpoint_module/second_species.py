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
        super(SecondSpecies, self).__init__(cf,ctp_position)
        self.cf = cf
        self.melody_rhythm = self.get_rhythm()
        self.short_cf = self.cf.melody
        self.cf_notes = [item for item in self.cf.melody for repetitions in range(2)]
        self.downbeats = self.get_downbeats()
        self.upbeats = self.get_upbeats()

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
        "Voices all move together in the same rhythm as the cantus firmus."
        return [4] * len(self.cf_notes)

    """ VOICE INDEPENDENCE RULES """

    def _is_parallel_perfects_on_downbeats(self,ctp_draft, upper_voice, lower_voice):
        db = self.downbeats
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

    """ DISSONANT RULES"""

    def dissonant_rules(self, ctp_draft):
        # In first species there is no dissonance, so the allowed harmonic intervals are consonances
        return 0

    """ HARMONIC RULES """

    def _is_valid_terminals(self, ctp_draft, cf_notes):
        # check start and end pitches and see if they are valid
        # must begin and end with perfect consonances (octaves, fifths or unison)
        # Octaves or unisons preferred at the end (i.e. perfect fifth not allowed)
        # if below, the start and end must be the octave the cf
        if self.ctp_position == "above":
            if (ctp_draft[0] - cf_notes[0] not in [Unison, P5, Octave]) or (
                    ctp_draft[-1] - cf_notes[-1] not in [Unison, Octave]):
                return False
            else:
                return True
        else:
            if (cf_notes[0] - ctp_draft[0] not in [Unison, Octave]) or (
                    cf_notes[-1] - ctp_draft[-1] not in [Unison, Octave]):
                return False
            else:
                return True

    def _no_outlined_tritone(self, ctp_draft):
        outline_idx = [0]
        outline_intervals = []
        not_allowed_intervals = [Tritone, m7, M7]
        # mellom ytterkant og inn + endring innad
        dir = [sign(ctp_draft[i + 1] - ctp_draft[i]) for i in range(len(ctp_draft) - 1)]
        for i in range(len(dir) - 1):
            if dir[i] != dir[i + 1]:
                outline_idx.append(i + 1)
        outline_idx.append(len(ctp_draft) - 1)
        # Iterate over the outline indices and check if a tritone is found
        for i in range(len(outline_idx) - 1):
            outline_intervals.append(abs(ctp_draft[outline_idx[i]] - ctp_draft[outline_idx[i + 1]]))

        for interval in not_allowed_intervals:
            if interval in outline_intervals:
                return False

        return True

    def harmonic_rules(self, ctp_draft, cf_notes):
        penalty = 0
        if not self._is_valid_terminals(ctp_draft, cf_notes):
            self.ctp_errors.append("Terminals not valid!")
            penalty += 100
        if not self._no_outlined_tritone(ctp_draft):
            self.ctp_errors.append("Outlined dissonant interval!")
            penalty += 100
        return penalty

    """ TOTAL PENALTY"""

    def total_penalty(self, ctp_draft, cf_notes):
        penalty = 0
        penalty += self.melodic_rules(ctp_draft)
        penalty += self.voice_independence_rules(ctp_draft, cf_notes)
        penalty += self.dissonant_rules(ctp_draft)
        penalty += self.harmonic_rules(ctp_draft, cf_notes)
        return penalty

    """ HELP FUNCTIONS FOR INITIALIZING COUNTERPOINT"""

    def _start_notes(self):
        if self.ctp_position == "above":
            return [self.cf_tonic, self.cf_tonic + P5, self.cf_tonic + Octave]
        else:
            return [self.cf_tonic - Octave, self.cf_tonic]

    def _end_notes(self):
        if self.ctp_position == "above":
            return [self.cf_tonic, self.cf_tonic + Octave]
        else:
            return [self.cf_tonic, self.cf_tonic - Octave]

    def _penultimate_notes(self, cf_end):  # Bug in penultimate
        if self.ctp_position == "above":
            s = 1
        else:
            s = -1
        if self.cf_direction[-1] == 1.0:
            penultimate = cf_end + 2
        else:
            penultimate = cf_end - 1
        return [penultimate, penultimate + s * Octave]

    def get_harmonic_possibilities(self, idx, cf_note):
        poss = super(SecondSpecies,self).get_harmonic_possibilities(cf_note)
        if idx in self.upbeats and idx != 1:
            for interval in self.dissonant_intervals:
                if self.ctp_position == "above":
                    if cf_note + interval in self.scale_pitches:
                        poss.append(cf_note + interval)
                else:
                    if cf_note - interval in self.scale_pitches:
                        poss.append(cf_note - interval)
        return poss

    def _possible_notes(self):
        poss = [None for elem in self.cf_notes]
        for i in range(len(self.cf_notes)):
            if i == 1 or i == 0:
                poss[i] = self._start_notes()
            elif i == len(self.cf_notes) - 3:
                poss[i] = self._penultimate_notes(self.cf_notes[i + 1])
            elif i == len(self.cf_notes) - 1 or i == len(self.cf_notes)-2:
                poss[i] = self._end_notes()
            else:
                poss[i] = self.get_harmonic_possibilities(i, self.cf_notes[i])
        return poss

    """ INITIALIZING COUNTERPOINT WITH RANDOM VALUES"""

    def _initialize_ctp(self):
        self.melody_rhythm = self.get_rhythm()
        poss = self._possible_notes()
        ctp_notes = []
        for p in poss:
            ctp_notes.append(rm.choice(p))
        return ctp_notes, poss
    def generate_ctp(self):
        cf_notes = self.cf_notes
        ctp_shell, poss = self._initialize_ctp()
        error, ctp_shell = self._search(ctp_shell,poss)
        self.ctp_notes = ctp_shell.copy()
        self.ctp_errors = []
        self.error = self.total_penalty(ctp_shell,cf_notes)
        print("ctp errors: ",self.ctp_errors)
        self.ctp_notes[0] = -1
        self.ctp_notes[-2] = self.ctp_notes[-1]
        self.ctp_notes.pop(-1)
        self.melody_rhythm.pop(-1)
        self.melody_rhythm[-1] = 8
        print("second species error:",self.error)
