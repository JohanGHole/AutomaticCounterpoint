import music_module.music as m
from counterpoint_module.cf import *
import search_algorithm.search_algorithm as Search_Algorithm

class Counterpoint:
    def __init__(self,cf,ctp_position = "above"):
        if ctp_position == "above":
            self.voice_range = RANGES[RANGES.index(cf.voice_range)+1]
        else:
            self.voice_range = RANGES[RANGES.index(cf.voice_range)-1]
        self.melody = m.Melody(cf.key,cf.scale,cf.bar_length, voice_range = self.voice_range)
        self.ctp_position = ctp_position
        self.scale_pitches = self.melody.scale_pitches
        self.cf = cf
        self.species = None
        self.search_domain = []
        self.ctp_errors = []
        self.MAX_SEARCH_TIME = 5

    """ VALID START, END, AND PENULTIMATE NOTES"""
    def _start_notes(self):
        cf_tonic = self.cf.pitches[0]
        if self.ctp_position == "above":
            if SPECIES[self.species] == 1:
                return [cf_tonic, cf_tonic + P5, cf_tonic + Octave]
            else:
                return [cf_tonic+P5,cf_tonic + Octave]
        else:
            if SPECIES[self.species] == 1:
                return [cf_tonic - Octave, cf_tonic]
            else:
                return [cf_tonic - Octave]

    def _end_notes(self):
        cf_tonic = self.cf.pitches[0]
        if self.ctp_position == "above":
            return [cf_tonic, cf_tonic + Octave]
        else:
            return [cf_tonic, cf_tonic - Octave]

    def _penultimate_notes(self, cf_end):
        cf_direction = [sign(self.cf.pitches[i] - self.cf.pitches[i - 1]) for i in range(1, len(self.cf.pitches))]
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
    def get_consonant_possibilities(self,cf_note):
        poss = []
        for interval in HARMONIC_CONSONANCES:
            if self.ctp_position == "above":
                if cf_note+interval in self.scale_pitches:
                    poss.append(cf_note+interval)
            else:
                if cf_note-interval in self.scale_pitches:
                    poss.append(cf_note-interval)
        return poss

    def randomize_ctp_melody(self):
        ctp_melody = []
        i = 0
        measure = 0
        while measure < len(self.melody.rhythm):
            note_duration = 0
            while note_duration < len(self.melody.rhythm[measure]):
                if i == 0:
                    ctp_melody.append(rm.choice(self.search_domain[i]))
                elif i > 0 and self.melody.ties[i-1] == True:
                    ctp_melody.append(ctp_melody[i-1])
                else:
                    ctp_melody.append(rm.choice(self.search_domain[i]))
                i += 1
                note_duration += 1
            measure += 1
        return ctp_melody

    """ GENERATE COUNTERPOINT PITCHES BY CALLING THE SEARCH ALGORITHM"""
    def generate_ctp(self):
        if self.species == None:
            print("No species to generate!")
        self.melody.set_melody(self.randomize_ctp_melody())
        self.ctp_errors = []
        self.error, best_ctp,self.ctp_errors = Search_Algorithm.improved_search(self)
        self.melody.set_melody(best_ctp)



