import music_module.music as m
import pretty_midi
from music_module.constants import *
import random as rm
import math
def sign(x):
    return math.copysign(1, x)

"""
This sub-module contains methods for generating a cantus firmus.

TODO:
    length of about 8–16 notes (check)
    arhythmic (all whole notes; no long or short notes) (check)
    begin and end on tonic
    approach final tonic by step (usually re–do, sometimes ti–do) (check)
    all note-to-note progressions are melodic consonances (check)
    range (interval between lowest and highest notes) of no more than a tenth, usually less than an octave (check)
    a single climax (high point) that appears only once in the melody (check)
    clear logical connection and smooth shape from beginning to climax to ending
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
    dissonant_intervals = [m2, M2, m7, M7, Tritone]
    consonant_intervals = [m2,M2,m3, M3, P4, P5, m6, Octave]

    def __init__(self,key, scale, bar_length, melody_notes=None, melody_rhythm = 8, start=0, voice_range = RANGES[ALTO]):
        super(Cantus_Firmus, self).__init__(key, scale, bar_length, melody_notes= melody_notes, melody_rhythm = melody_rhythm,
                                            start = start, voice_range = voice_range)
        self.start_note = self._start_note()
        self.end_note = self.start_note
        self.penultimate_note = self._penultimate_note()
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
        start_note_eval = []

        for notes in possible_start_notes:
            start_note_eval.append(abs(v_range.index(notes) / len(v_range)-0.5)) # eval based on most median possibility since this gives maximum "wiggle room"
        start_note_score = min(start_note_eval)
        start_note = possible_start_notes[(start_note_eval.index(start_note_score))]

        return start_note

    def _penultimate_note(self):
        """ The last note can be approached from above or below.
            It is however most common that the last note is approached from above
        """
        leading_tone = self.start_note - 1
        super_tonic = self.start_note + 2
        weights = [0.1,0.9] # it is more common that the penultimate note is the supertonic than leading tone
        penultimate_note = rm.choices([leading_tone,super_tonic],weights)[0]
        return penultimate_note

    def _generate_length(self):
        """
        Generates the number of bars for the cantus firmus. Length between 8 and 16 bars, with 12 being most common.
        Therefore modelled as a normal distribution with mean value = 12
        :return:
        """
        random_length = rm.normalvariate(12,2.2)
        return round(random_length)

    def _possible_notes(self):
        """
        Must be within a tenth of the lowest note
        :return:
        """
        """
        First pick the lowest note. If index out of range, the tonic
        cannot be the lowest. Iteratively change the range until all notes are within the voice range, then return these
        values.
        """
        poss = []
        sn_idx = self.scale_pitches.index(self.start_note)
        range_from_tonic = len(self.scale_pitches) - sn_idx
        if range_from_tonic < 10:
            low_range = sn_idx - (10-range_from_tonic)
            top_range = sn_idx + range_from_tonic
        else:
            low_range = sn_idx
            top_range = sn_idx+10
        for i in range(low_range,top_range): # maximum range of a tenth
            poss.append(self.scale_pitches[i])
        return poss

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

    def _pick_climax(self,length,poss):
        """
        :length: the length of the cantus firmus
        :return: the peak and corresponding index value of the peak
        """
        """
        TODO:
            Might need a better suited algorithm
        """
        tonic_idx = poss.index(self.start_note)
        climax_indices = [idx for idx in range(2,length-3)]
        lowest_note = poss[0]
        climax = rm.choice(poss[tonic_idx+2:]) # The tonic and supertonic cannot be climax
        idx = rm.choice(climax_indices)
        return climax, idx


    def _initialize_cf(self):
        """
        Sets up the skeleton of the cf. This includes start note, end note, penultimate note and climax
        This reflects how most cf composition exercises are structured
        :return: list of cf notes. "None" is a placeholder.
        """
        start_note = self.start_note
        end_note = self.end_note
        penultimate_note = self._penultimate_note()
        length = self._generate_length()
        cf_shell = [None for i in range(length)]
        cf_shell[0] = start_note
        cf_shell[-1] = end_note
        cf_shell[-2] = penultimate_note
        poss = self._possible_notes()
        climax, climax_idx = self._pick_climax(length, poss)
        cf_shell[climax_idx] = climax
        poss.remove(climax)
        return cf_shell,poss,climax_idx, climax

    def _parse_shell(self,cf_shell,climax_goal):
        start_note = cf_shell[0]
        penultimate_note = cf_shell[-2]
        climax = None
        climax_idx = None
        for i in range(2,len(cf_shell)-2):
            if cf_shell[i] != None:
                climax = cf_shell[i]
                climax_idx = i
                break
        if climax_goal:
            return start_note, 0, climax,climax_idx
        else:
            return climax, climax_idx,penultimate_note,len(cf_shell)-2

    def _get_melodic_consonances(self,prev_note,poss, climax):
        mel_cons = []
        for i in range(len(consonant_melodic_intervals)):
            if prev_note+consonant_melodic_intervals[i] in poss:
                mel_cons.append(prev_note+consonant_melodic_intervals[i])
            if prev_note-consonant_melodic_intervals[i] in poss and consonant_melodic_intervals[i] != m6:
                mel_cons.append(prev_note-consonant_melodic_intervals[i])
        for notes in mel_cons:
            if notes >= climax:
                mel_cons.remove(notes)
            if notes == prev_note:
                mel_cons.remove(notes)
        return mel_cons

    def _get_best_local_option(self,prev_note,prev_prev_note):
        # returns the best local option based on score
        if prev_prev_note is None:
            # return step or small leap
            print("no prev_prev_note ")
        if self._is_large_leap(prev_note,prev_prev_note):
            # Resolve by step in opposite direction
            print("large leap")

    def _group_consonances(self, prev_note, mel_cons):
        steps = []
        small_leaps = []
        large_leaps = []
        for note in mel_cons:
            if self._is_step(note,prev_note):
                steps.append(note)
            elif self._is_small_leap(note,prev_note):
                small_leaps.append(note)
            elif self._is_large_leap(note,prev_note):
                large_leaps.append(prev_note)
        return steps,small_leaps,large_leaps

    def _pre_climax_contour(self,cf_shell,climax):
        tonic = cf_shell[0]
        leading_tone = tonic+M7
        num_notes = cf_shell.index(climax)-cf_shell.index(tonic)
        diatonic_steps = self.scale_pitches.index(climax)-self.scale_pitches.index(tonic)
        print("diatonic steps: ",diatonic_steps)
        print("num notes: ",num_notes)
        max_contour_sum = diatonic_steps
        contour = []
        for i in range(num_notes):
            if sum(contour) < max_contour_sum-1:
                contour.append(1)
            else:
                contour.append(-1)
            print("sum contour: ",sum(contour))
            if i == num_notes -1 and sum(contour) < max_contour_sum:
                contour[i] += max_contour_sum-sum(contour)
        step_sum = sum(contour)
        small_leaps_needed = step_sum - diatonic_steps
        for i in range(abs(small_leaps_needed)):
            for j in range(len(contour)):
                if sign(contour[i]) == sign(small_leaps_needed):
                    if sum(contour[:len(contour)-2])+1 == diatonic_steps:
                        print("climax is reached before the designated time")
                    else:
                        contour[i] += small_leaps_needed
                    break
        print(contour)
        print("leaps needed: ",small_leaps_needed)
        for i in range(1,cf_shell.index(climax)):
            prev_note_idx = self.scale_pitches.index(cf_shell[i-1])
            cf_shell[i] = self.scale_pitches[prev_note_idx+contour[i-1]]

        # ascending line, descending or both?
        # possible outline: in diatonic steps from tonic. +1,+1,+2,-1,+1,+1,+1
        # sum outline = diatonic_steps
        # the sum must be the number of diatonic steps
        # the penultimate sum can never be higher than diatonic_steps -1
        # small_leap upwards possible?
        # small_leap downwards possible?
        #


    def generate_cf(self):
        #cf_shell, poss, climax_idx, climax = self._initialize_cf()
        cf_shell = [60, None, None, None, None, 67, None, None, 62,60]
        poss = self._possible_notes()
        climax = 67
        climax_idx = 5
        cf_shell[climax_idx] = climax
        poss.remove(climax)
        print("whole voice range: ",self.scale_pitches)
        print("possible notes: ",self.scale_pitches)
        print("The shell: ", cf_shell)
        self._pre_climax_contour(cf_shell,climax)
        print("new shell: ",cf_shell)
        for i in range(climax_idx, len(cf_shell) - 2):
            prev_note = cf_shell[i-1]
            mel_cons = self._get_melodic_consonances(prev_note, self.scale_pitches, climax)
            steps, small_leaps, large_leaps = self._group_consonances(prev_note,mel_cons)
            print("test: ", mel_cons)
            print("steps: ",steps)
            print("small leaps: ",small_leaps)
            if i != climax_idx:
                if rm.randint(1,100) > 25:
                    next_note = rm.choice(steps)
                else:
                    next_note = rm.choice(small_leaps)
                cf_shell[i] = next_note
                prev_note = next_note
            print("Current shell: ", cf_shell)

        self.melody = cf_shell

"""
for i in range(1):
    cf = Cantus_Firmus(KEY_NAMES[i],"major",bar_length=8,voice_range=RANGES[TENOR])
    cf.generate_cf()
    inst = pretty_midi.Instrument(program=pretty_midi.instrument_name_to_program("violin"), is_drum=False, name="Cf")
    cf.to_instrument(inst, time=1, start=0)
    m.export_to_midi(inst, tempo=120.0, name="cantus_firmus/" + cf.key + "_v3.mid")

start and stop notes - must be the tonic (key) in valid range. 

"""