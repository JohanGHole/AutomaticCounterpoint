import music_module.music as m
import pretty_midi
from music_module.constants import *
import random as rm
import math
from time import time

class Cantus_Firmus(m.Melody):
    # Some constants for easy access
    perfect_intervals = [Unison, P5, Octave]
    dissonant_intervals = [m7, M7, Tritone,-m6,-m7,-M7]
    consonant_melodic_intervals = [m2,M2,m3, M3, P4, P5, m6, Octave,-m2,-M2,-m3,-M3,-P4,-P5,-Octave]

    def __init__(self,key, scale, bar_length, melody_notes=None, melody_rhythm = None, start=0, voice_range = RANGES[ALTO]):
        super(Cantus_Firmus, self).__init__(key, scale, bar_length, melody_notes= melody_notes, melody_rhythm = melody_rhythm,
                                            start = start, voice_range = voice_range)
        self.cf_errors = []

        """ Music representation"""
        self.rhythm = self._generate_rhythm()
        self.ties = [False]*len(self.rhythm)
        self.pitches = self._generate_cf()
        self.length = len(self.rhythm)
    def _start_note(self):
        root = self.key
        try:
            root_idx = KEY_NAMES.index(root)
        except:
            root_idx = KEY_NAMES_SHARP.index(root)
        v_range = self.voice_range
        possible_start_notes = []
        for pitches in v_range:
            if pitches % Octave == root_idx:
                possible_start_notes.append(pitches)
        tonics = possible_start_notes
        return tonics,possible_start_notes[0]

    def _penultimate_note(self):
        """ The last note can be approached from above or below.
            It is however most common that the last note is approached from above
        """
        leading_tone = self._start_note()[1] - 1
        super_tonic = self._start_note()[1] + 2
        weights = [0.1,0.9] # it is more common that the penultimate note is the supertonic than leading tone
        penultimate_note = rm.choices([leading_tone,super_tonic],weights)[0]
        return penultimate_note

    def _get_leading_tones(self):
        if self.scale_name == "minor":
            leading_tone = self._start_note()[1] - 2
        else:
            leading_tone = self._start_note()[1] - 1
        return [leading_tone]

    def _generate_rhythm(self):
        """
        Generates the number of bars for the cantus firmus. Length between 8 and 13 bars, with 12 being most common.
        Therefore modelled as a uniform distribution over 8 to 14
        :return:
        """
        random_length = rm.randint(8,14)
        return [(8,)]*random_length

    def _is_step(self,note,prev_note):
        if abs(prev_note-note) in [m2, M2]:
            return True
        else:
            return False

    def _is_small_leap(self,note, prev_note):
        if abs(prev_note-note) in [m3, M3]:
            return True
        else:
            return False

    def _is_large_leap(self,note,prev_note):
        if abs(prev_note-note) >= P4:
            return True
        else:
            return False

    """ RULES FOR THE CANTUS FIRMUS"""
    def _is_climax(self,cf_shell):
        if cf_shell.count(max(cf_shell)) == 1:
            return True
        else:
            return False

    def _is_resolved_leading_tone(self,cf_shell):
        tonics = self._start_note()[0]
        leading_tones = self._get_leading_tones()
        for leading_tone in leading_tones:
            if leading_tone in cf_shell and cf_shell[cf_shell.index(leading_tone)+1] != tonics[0]:
                return False
        return True

    def _is_dissonant_intervals(self,cf_shell):
        for i in range(len(cf_shell)-1):
            if cf_shell[i+1] -cf_shell[i] in self.dissonant_intervals:
                return True
        return False

    def _check_leaps(self,cf_shell):
        penalty = 0
        num_large_leaps = 0
        for i in range(len(cf_shell)-2):
            if self._is_large_leap(cf_shell[i],cf_shell[i+1]):
                num_large_leaps += 1
                if abs(cf_shell[i]-cf_shell[i+1]) == Octave:
                    # small penalty for octave leap
                    self.cf_errors.append("penalty for octave leap")
                    penalty += 50
                # Check consecutive leaps first
                elif self._is_large_leap(cf_shell[i+1],cf_shell[i+2]):
                    self.cf_errors.append("consecutive leaps")
                    penalty += 25
                elif self._is_large_leap(cf_shell[i+1],cf_shell[i+2]) and sign(cf_shell[i+1]-cf_shell[i]) != sign(cf_shell[i+2]-cf_shell[i+1]):
                    self.cf_errors.append("Large leaps in opposite direction")
                    penalty += 75
                elif self._is_step(cf_shell[i+1],cf_shell[i+2]) and sign(cf_shell[i+1]-cf_shell[i]) == sign(cf_shell[i+2]-cf_shell[i+1]):
                    self.cf_errors.append("A leap is not properly recovered")
                    penalty += 75
        if num_large_leaps >= int(len(self.rhythm) /2) - 2:
            penalty += 100
        return penalty

    def _is_valid_note_count(self,cf_shell):
        for notes in set(cf_shell):
            if cf_shell.count(notes) > 4:
                return False
            else:
                return True

    def _is_valid_range(self,cf_shell):
        if abs(max(cf_shell)-min(cf_shell)) > Octave+M3:
            return False
        else:
            return True

    def _is_repeated_motifs(self,cf_shell):
        paired_notes = []
        for i in range(len(cf_shell)-1):
            if cf_shell[i] == cf_shell[i+1]:
                return True
            if cf_shell[i] == cf_shell[0] and i != 0:
                return True
            paired_notes.append([cf_shell[i],cf_shell[i+1]])
        for pairs in paired_notes:
            if paired_notes.count(pairs) > 1:
                return True
        return False

    def _cost_function(self,cf_shell):
        penalty = 0
        penalty = self._check_leaps(cf_shell)
        if not self._is_valid_note_count(cf_shell):
            self.cf_errors.append("note repetition")
            penalty += 100
        if not self._is_climax(cf_shell):
            self.cf_errors.append("no unique cf climax")
            penalty += 100
        if not self._is_valid_range(cf_shell):
            self.cf_errors.append("exceeds the range of a tenth")
            penalty += 100
        if self._is_repeated_motifs(cf_shell):
            self.cf_errors.append("motivic repetitions")
            penalty += 100
        if not self._is_resolved_leading_tone(cf_shell):
            self.cf_errors.append("leading tone not resolved")
            penalty += 100
        if self._is_dissonant_intervals(cf_shell):
            self.cf_errors.append("dissonant interval")
            penalty += 100
        return penalty

    def _initialize_cf(self):
        """
        Randomizes the initial cf and sets correct start, end, and penultimate notes.
        :return: list of cf pitches.
        """
        start_note = self._start_note()[1]
        end_note = start_note
        penultimate_note = self._penultimate_note()
        length = len(self.rhythm)
        cf_shell = [rm.choice(self.scale_pitches) for i in range(length)]
        cf_shell[0] = start_note
        cf_shell[-1] = end_note
        cf_shell[-2] = penultimate_note
        return cf_shell

    def _get_melodic_consonances(self,prev_note):
        mel_cons = []
        for intervals in self.consonant_melodic_intervals:
            if prev_note+intervals in self.scale_pitches:
                mel_cons.append(prev_note+intervals)
        # To further randomize the generated results, the melodic consonances are shuffled
        rm.shuffle(mel_cons)
        return mel_cons

    def _generate_cf(self):
        total_penalty = math.inf
        iteration = 0
        while total_penalty > 0:
            cf_shell = self._initialize_cf() # initialized randomly
            for i in range(1,len(cf_shell)-2):
                self.cf_errors = []
                local_max = math.inf
                cf_draft = cf_shell.copy()
                mel_cons = self._get_melodic_consonances(cf_shell[i-1])
                for notes in mel_cons:
                    cf_draft[i] = notes
                    local_penalty = self._cost_function(cf_draft)
                    if local_penalty <= local_max:
                        local_max = local_penalty
                        best_choice = notes
                cf_shell[i] = best_choice
            self.cf_errors = []
            total_penalty = self._cost_function(cf_shell)
            iteration += 1
        return cf_shell.copy()



