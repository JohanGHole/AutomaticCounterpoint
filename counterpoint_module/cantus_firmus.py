import music_module.music as m
from music_module.constants import *
import random as rm
"""
This sub-module contains methods for generating a cantus firmus.

TODO:
    length of about 8–16 notes (check)
    arhythmic (all whole notes; no long or short notes) (check)
    begin and end on tonic
    approach final tonic by step (usually re–do, sometimes ti–do)
    all note-to-note progressions are melodic consonances
    range (interval between lowest and highest notes) of no more than a tenth, usually less than an octave
    a single climax (high point) that appears only once in the melody
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
    consonant_intervals = [m3, M3, P4, P5, m6, M6, Octave]

    def _start_note(self):
        """

        :return: The optimal start note for the cantus firmus given the key and voice range
        """
        root = self.key
        try:
            root_idx = KEY_NAMES.index(root)
        except:
            root_idx = KEY_NAMES_SHARP.index(root)
        v_range = self.vocal_range
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

    def _generate_length(self):
        """
        Generates the number of bars for the cantus firmus. Length between 8 and 16 bars, with 12 being most common.
        Therefore modelled as a normal distribution with mean value = 12
        :return:
        """
        random_length = rm.normalvariate(12,2.2)
        return round(random_length)
    def _initialize_cf(self,tonic,length):


    def generate_cf(self):
        print("hello")
        tonic = self._start_note()
        length = self._generate_length()




cf = Cantus_Firmus("A","minor",bar_length=1,vocal_range=RANGES[BASS])
cf.generate_cf()
"""
start and stop notes - must be the tonic (key) in valid range. 

"""