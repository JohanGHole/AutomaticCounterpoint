import music_module.music as m
import pretty_midi
from music_module.constants import *
import random as rm
import math
from time import time
def sign(x):
    return math.copysign(1, x)

"""
This sub-module contains methods for generating a cantus firmus.

TODO:
    length of about 8–16 notes (check)
    arhythmic (all whole notes; no long or short notes) (check)
    begin and end on tonic (check)
    approach final tonic by step (usually re–do, sometimes ti–do) (check)
    all note-to-note progressions are melodic consonances (check)
    range (interval between lowest and highest notes) of no more than a tenth, usually less than an octave (check)
    a single climax (high point) that appears only once in the melody (check)
    clear logical connection and smooth shape from beginning to climax to ending (check) (prioritize steps)
    mostly stepwise motion, but with some leaps (mostly small leaps)
    no repetition of “motives” or “licks”
    any large leaps (fourth or larger) are followed by step in opposite direction
    no more than two leaps in a row; no consecutive leaps in the same direction (Fux’s F-major cantus is an exception, where the back-to-back descending leaps outline a consonant triad.)
    the leading tone progresses to the tonic
    in minor, the leading tone only appears in the penultimate bar; the raised submediant is only used when progressing to that leading tone
"""

class Cantus_Firmus(m.Melody):
    # Some constants for easy access
    perfect_intervals = [Unison, P5, Octave]
    dissonant_intervals = [m7, M7, Tritone,-m6,-m7,-M7]
    consonant_melodic_intervals = [m2,M2,m3, M3, P4, P5, m6, Octave,-m2,-M2,-m3,-M3,-P4,-P5,-Octave]

    def __init__(self,key, scale, bar_length, melody_notes=None, melody_rhythm = None, start=0, voice_range = RANGES[ALTO]):
        super(Cantus_Firmus, self).__init__(key, scale, bar_length, melody_notes= melody_notes, melody_rhythm = melody_rhythm,
                                            start = start, voice_range = voice_range)
        self.tonics = []
        self.start_note = self._start_note()
        self.end_note = self.start_note
        self.leading_tones = self._get_leading_tones()
        self.penultimate_note = self._penultimate_note()
        self.length = self._generate_length()
        if melody_rhythm != None:
            self.melody_rhythm = melody_rhythm
        else:
            self.melody_rhythm = [8]*self.length
        self.cf_errors = []
    def _start_note(self):
        """

        :return: The optimal start note for the cantus firmus given the key and voice range
        """
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
        self.tonics = possible_start_notes
        print("tonics: ",self.tonics)
        """
        for notes in possible_start_notes:
            if self.scale_pitches.index(notes) <= 1:
                possible_start_notes.remove(notes)
        """
        print("tonics after: ",self.tonics)
        return possible_start_notes[0]

    def _penultimate_note(self):
        """ The last note can be approached from above or below.
            It is however most common that the last note is approached from above
        """
        leading_tone = self.start_note - 1
        super_tonic = self.start_note + 2
        weights = [0.1,0.9] # it is more common that the penultimate note is the supertonic than leading tone
        penultimate_note = rm.choices([leading_tone,super_tonic],weights)[0]
        return penultimate_note
    def _get_leading_tones(self):
        if self.scale_name == "minor":
            leading_tone = self.start_note - 2
        else:
            leading_tone = self.start_note - 1
        return [leading_tone, leading_tone+Octave]
    def _generate_length(self):
        """
        Generates the number of bars for the cantus firmus. Length between 8 and 16 bars, with 12 being most common.
        Therefore modelled as a uniform distribution over 8 to 12
        :return:
        """
        random_length = rm.randint(8,12)
        return round(random_length)

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

    """ GLOBAL RULES FOR THE CANTUS FIRMUS"""
    def _has_climax(self,cf_shell):
        if cf_shell.count(max(cf_shell)) == 1:
            return 0
        else:
            return 200

    def _resolved_leading_tone(self,cf_shell):
        for leading_tone in self.leading_tones:
            if leading_tone in cf_shell and cf_shell[cf_shell.index(leading_tone)+1] not in self.tonics:
                self.cf_errors.append("Leading tone not properly resolved")
                return 150
        return 0

    def _check_dissonant_intervals(self,cf_shell):
        for i in range(len(cf_shell)-1):
            if cf_shell[i+1] -cf_shell[i] in self.dissonant_intervals:
                self.cf_errors.append("dissonant interval")
                return 150
        return 0

    def _global_leap_score(self,cf_shell):
        score = 0
        num_large_leaps = 0
        for i in range(len(cf_shell)-2):
            if self._is_large_leap(cf_shell[i],cf_shell[i+1]):
                num_large_leaps += 1
                if abs(cf_shell[i]-cf_shell[i+1]) == Octave:
                    # small penalty for octave leap
                    self.cf_errors.append("penalty for octave leap")
                    score += 75
                # Check consecutive leaps first
                elif self._is_small_leap(cf_shell[i+1],cf_shell[i+2]):
                    score +=50
                    self.cf_errors.append("large conescutive leaps")
                elif self._is_large_leap(cf_shell[i+1],cf_shell[i+2]) and sign(cf_shell[i+1]-cf_shell[i]) != sign(cf_shell[i+2]-cf_shell[i+1]):
                    score += 100
                    self.cf_errors.append("Large leaps in opposite direction")
                elif self._is_step(cf_shell[i+1],cf_shell[i+2]) and sign(cf_shell[i+1]-cf_shell[i]) == sign(cf_shell[i+2]-cf_shell[i+1]):
                    score += 100
                    self.cf_errors.append("A leap is not properly recovered")
        if num_large_leaps >= int(self.length /2) - 2:
            score += 150
        return score, num_large_leaps

    def _repeated_notes(self,cf_shell):
        for notes in set(cf_shell):
            if cf_shell.count(notes) > 4:
                self.cf_errors.append("Too many note repetitions")
                return 100
            else:
                return 0

    def _valid_range(self,cf_shell):
        if abs(max(cf_shell)-min(cf_shell)) > Octave+M3:
            self.cf_errors.append("Range too wide")
            return 150
        else:
            return 0
    def _repeated_motifs(self,cf_shell):
        paired_notes = []
        score = 0
        for i in range(len(cf_shell)-1):
            if cf_shell[i] == cf_shell[i+1]:
                self.cf_errors.append("repeated note")
                score += 50
            if cf_shell[i] == cf_shell[0] and i != 0:
                self.cf_errors.append("tonic in wrong position")
                score += 50
            paired_notes.append([cf_shell[i],cf_shell[i+1]])
        for pairs in paired_notes:
            if paired_notes.count(pairs) > 1:
                self.cf_errors.append("repeated motives")
                score += 100
        return score
    def _global_penalty(self,cf_shell):
        global_penalty = 0
        penalty, num_large_leaps = self._global_leap_score(cf_shell)
        global_penalty+= penalty
        penalty = self._repeated_notes(cf_shell)
        global_penalty += penalty
        penalty = self._has_climax(cf_shell)
        global_penalty += penalty
        penalty = self._valid_range(cf_shell)
        global_penalty += penalty
        penalty = self._repeated_motifs(cf_shell)
        global_penalty += penalty
        penalty = self._resolved_leading_tone(cf_shell)
        global_penalty += penalty
        penalty = self._check_dissonant_intervals(cf_shell)
        global_penalty += penalty
        return global_penalty

    def _local_penalty(self,note,prev_note):
        penalty = 0
        if self._is_large_leap(note,prev_note):
            if abs(note-prev_note) >= m6:
                penalty += 100
            else:
                penalty += 50
        if note == prev_note:
            penalty += 25
        return penalty
    def _initialize_cf(self):
        """
        Randomizes the initial cf and sets correct start, end, and penultimate notes.
        :return: list of cf notes.
        """
        start_note = self.start_note
        end_note = self.end_note
        penultimate_note = self._penultimate_note()
        length = self.length
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

    def generate_cf(self):
        t0 = time()
        total_penalty = math.inf
        iteration = 0
        while total_penalty > 0:
            total_penalty = 0
            cf_shell = self._initialize_cf() # initialized randomly
            for i in range(1,len(cf_shell)-2):
                self.cf_errors = []
                local_max = math.inf
                cf_draft = cf_shell.copy()
                mel_cons = self._get_melodic_consonances(cf_shell[i-1])
                for notes in mel_cons:
                    cf_draft[i] = notes
                    local_penalty = self._global_penalty(cf_draft)
                    local_penalty += self._local_penalty(cf_draft[i],cf_draft[i-1])
                    if local_penalty <= local_max:
                        local_max = local_penalty
                        best_choice = notes
                cf_shell[i] = best_choice
            self.cf_errors = []
            total_penalty += self._global_penalty(cf_shell)
            iteration += 1
            print("iter: ",iteration)
        print("errors: ",self.cf_errors)
        print(cf_shell)
        self.melody = cf_shell
        t1 = time()
        print("total comp time: ",str((t1-t0)*1000)+"ms")

"""
for i in range(1):
    cf = Cantus_Firmus(KEY_NAMES[i],"minor",bar_length=8,voice_range=RANGES[ALTO])
    cf.generate_cf()
    inst = pretty_midi.Instrument(program=pretty_midi.instrument_name_to_program("violin"), is_drum=False, name="Cf")
    cf.to_instrument(inst, time=1, start=0)
    m.export_to_midi(inst, tempo=120.0, name="cantus_firmus/" + cf.key + "_new_cf.mid")
"""


