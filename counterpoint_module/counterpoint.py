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
    dissonant_intervals = [m2,M2,P4,M7,m7,P8+m2,P8+M2]
    harmonic_consonances = [m3,M3,P5,m6,M6,P8,P8+m3,P8+M3]
    perfect_intervals = [P5,P8]
    def __init__(self,cf,ctp_position = "above"):
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
        self.ctp = m.Melody(cf.key,cf.scale,cf.bar_length,melody_notes=None,melody_rhythm=None,ties = False, start = 0, voice_range = self.voice_range)
        self.ctp_position = ctp_position
        self.scale_pitches = self.ctp.scale_pitches
        self.cf = cf
        self.species = None
        self.search_domain = []
        self.ctp_errors = []
        self.ERROR_THRESHOLD = 50
        self.MAX_SEARCH_WIDTH = 4
        self.MAX_SEARCH_TIME = 5
    """ RHYTHM """
    def get_rhythm(self):
        return [(8,)]*len(self.cf.melody)

    """ VALID START, END, AND PENULTIMATE NOTES"""
    def _start_notes(self):
        cf_tonic = self.cf.start_note
        if self.ctp_position == "above":
            return [cf_tonic, cf_tonic + P5, cf_tonic + Octave]
        else:
            return [cf_tonic - Octave, cf_tonic]

    def _end_notes(self):
        cf_tonic = self.cf.start_note
        if self.ctp_position == "above":
            return [cf_tonic, cf_tonic + Octave]
        else:
            return [cf_tonic, cf_tonic - Octave]

    def _penultimate_notes(self, cf_end):  # Bug in penultimate
        cf_direction = [sign(self.cf.melody[i] - self.cf.melody[i - 1]) for i in range(1, len(self.cf.melody))]
        if self.ctp_position == "above":
            s = 1
        else:
            s = -1
        if cf_direction[-1] == 1.0:
            penultimate = cf_end + 2
        else:
            penultimate = cf_end - 1
        return [penultimate, penultimate + s * Octave]

    """ INITIALIZING COUNTERPOINT WITH RANDOM VALUES"""

    def _initialize_ctp(self):
        self.ctp.melody_rhythm = self.get_rhythm()
        poss = self._possible_notes()
        ctp_shell = []
        for p in poss:
            ctp_shell.append(rm.choice(p))
        self.ctp.melody = ctp_shell.copy()
        return self.ctp, poss

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
    def _possible_notes(self):
        poss = []
        for i in range(len(self.cf_notes)):
            poss.append(self.get_consonant_possibilities(self.cf_notes[i]))
        return poss

    def post_ornaments(self):
        return

    def randomize_ctp_melody(self):
        ctp_melody = []
        i = 0
        measure = 0
        while measure < len(self.ctp.melody_rhythm):
            note_duration = 0
            while note_duration < len(self.ctp.melody_rhythm[measure]):
                if i == 0:
                    ctp_melody.append(rm.choice(self.search_domain[i]))
                elif i > 0 and self.ctp.ties[i-1] == True:
                    ctp_melody.append(ctp_melody[-1])
                else:
                    ctp_melody.append(rm.choice(self.search_domain[i]))
                i += 1
                note_duration += 1
            measure += 1
        return ctp_melody

    def generate_ctp(self, post_ornaments = True):
        if self.species == None:
            print("No species to generate!")

        self.ctp.set_melody(self.randomize_ctp_melody())
        self.ctp_errors = []
        self.error, best_ctp,self.ctp_errors = Search_Algorithm.improved_search(self)
        self.ctp.set_melody(best_ctp)
        global_score = self.error
        print("error score:",self.error)
        print("ctp errors: ",self.ctp_errors)
        if post_ornaments:
            self.post_ornaments()

    def construct_ctp_melody(self,start = 0):
        self.ctp_melody = m.Melody(self.key,self.scale,self.cf.bar_length,melody_notes=self.ctp_notes,melody_rhythm = self.melody_rhythm,start = start,voice_range = self.voice_range)
        return self.ctp_melody



