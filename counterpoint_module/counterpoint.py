import music_module.music as m
from counterpoint_module.cf import *
import math
import search_algorithm.search_algorithm as Search_Algorithm
"""
Harmonic_rules
melodic_rules
voice_independence_rules

MELODIC
- No leap larger than a fifth, except for octave and ascending minor sixth
- No successive same-direction leaps in the same voice unless they outline a triad. If they can't be avoided; they should total less than an octave
-  Leaps greater than a fifth should be compensated by movement in the opposite direction. If the leap is ascending make sure the compensation is stepwise.
- A leap of an octave should be balanced: preceded and followed by notes within the octave.
- No voice should move by a chromatic interval (any augmented or diminished interval).
- Avoid repeating a pitch when possible, especially in the lowest voice. In upper parts you can repeat a pitch as many as three times successively if necessary.
- Keep each voice confined to a singable range for the part, preferably not exceeding a tenth from its highest to its lowest pitch.
RHYTHM
- Voices all move together in the same rhythm as the cantus firmus. For traditional exercises all notes are whole notes.
- return [8]*len(cf)
"""


class Counterpoint:
    melodic_intervals = [Unison,m2,M2,m3,M3,P4,P5,P8,-m2,-M2,-m3,-M3,-P4,-P5,-P8]
    dissonant_intervals = [m2,M2,M7,m7,P8+m2,P8+M2]
    harmonic_consonances = [m3,M3,P5,m6,M6,P8,P8+m3,P8+M3]
    perfect_intervals = [P5,P8]
    def __init__(self,cf,ctp_position = "above"):
        self.key = cf.key
        self.cf = cf
        self.species = None
        self.melody_rhythm = cf.melody_rhythm.copy()
        self.scale_name = cf.scale_name
        self.ctp_position = ctp_position
        self.cf_notes = cf.melody
        self.cf_rhythm = cf.melody_rhythm
        if ctp_position == "above":
            try:
                self.voice_range = RANGES[RANGES.index(cf.voice_range)+1]
            except:
                print("ERROR. the Cantus Firmus is in the top voice. Writing ctp below instead..")
                self.voice_range = RANGES[RANGES.index(cf.voice_range)-1]
        else:
            try:
                self.voice_range = RANGES[RANGES.index(cf.voice_range)-1]
            except:
                print("ERROR. the Cantus Firmus is in the lowest voice. Writing ctp above instead..")
                self.voice_range = RANGES[RANGES.index(cf.voice_range)+1]
        self.scale = m.Scale(self.key,self.scale_name, self.voice_range)
        self.scale_pitches = self.scale.get_scale_pitches()
        self.ctp_notes = [None for elem in self.cf_notes]
        self.ctp_tonic = cf.start_note+(RANGES.index(self.voice_range)-RANGES.index(cf.voice_range))*Octave
        self.cf_tonic = cf.start_note
        self.cf_direction = [sign(self.cf_notes[i]-self.cf_notes[i-1]) for i in range(1,len(self.cf_notes))]
        self.ctp_melody = None
        self.ctp_errors = []
        self.ERROR_THRESHOLD = 50
        self.error_idx = []
        self.MAX_SEARCH_WIDTH = 4
    """ RHYTHM """
    def get_rhythm(self):
        return

    """ VALID START, END, AND PENULTIMATE NOTES"""
    def _start_notes(self):
        if self.ctp_position == "above":
            return [self.cf_tonic,self.cf_tonic + P5, self.cf_tonic + Octave]
        else:
            return [self.cf_tonic - Octave,self.cf_tonic]

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
    """ INITIALIZING COUNTERPOINT WITH RANDOM VALUES"""

    def _initialize_ctp(self):
        self.melody_rhythm = self.get_rhythm()
        cf_notes = self.cf_notes
        poss = self._possible_notes()
        return cf_notes, poss
    def get_consonant_possibilities(self,cf_note):
        poss = []
        for interval in self.harmonic_consonances:
            if self.ctp_position == "above":
                if cf_note+interval in self.scale_pitches:
                    poss.append(cf_note+interval)
            else:
                if cf_note-interval in self.scale_pitches:
                    poss.append(cf_note-interval)
        return poss

    def post_ornaments(self):
        return

    def generate_ctp(self, post_ornaments = True):
        if self.species == None:
            print("No species to generate!")
        global_score = math.inf
        counter = 0
        cf_notes, poss = self._initialize_ctp()
        while global_score > self.ERROR_THRESHOLD and counter < 5:
            # initialize random ctp based on the list of possibilities
            counter += 1
            ctp_shell = []
            for p in poss:
                ctp_shell.append(rm.choice(p))
            self.ctp_errors = []
            self.error, ctp_shell,self.ctp_errors = Search_Algorithm.search(self.species,ctp_shell,cf_notes,poss,self.scale_pitches,self.ctp_position,MAX_SEARCH_WIDTH=self.MAX_SEARCH_WIDTH,ERROR_THRESHOLD=self.ERROR_THRESHOLD)
            self.ctp_notes = ctp_shell.copy()
            global_score = self.error
        print("error score:",self.error)
        print("ctp errors: ",self.ctp_errors)
        if post_ornaments:
            self.post_ornaments()

    def construct_ctp_melody(self,start = 0):
        self.ctp_melody = m.Melody(self.key,self.scale,self.cf.bar_length,melody_notes=self.ctp_notes,melody_rhythm = self.melody_rhythm,start = start,voice_range = self.voice_range)
        return self.ctp_melody



