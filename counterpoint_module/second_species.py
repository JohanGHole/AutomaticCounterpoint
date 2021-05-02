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
        self.generate_ctp()
        print(self.melody_rhythm)
        self._expand_ctp()
        self.cf = cf
        self.expanded_cf = [item for item in self.cf.melody for repetitions in range(2)]
        self._new_rules()

    def _expand_ctp(self):
        notes = self.ctp_notes
        rhythm = self.melody_rhythm
        rhythm = [4]*len(rhythm)*2
        print(rhythm)
        notes_expanded = []
        notes = [ item for item in notes for repetitions in range(2) ]
        print(notes)
        self.melody_rhythm = rhythm
        self.ctp_notes = notes


    def _get_dissonant_possibilities(self,idx):
        if idx == len(self.ctp_notes)-1:
            return None
        interval = self.ctp_notes[idx+1]-self.ctp_notes[idx-1]
        poss = []
        if abs(interval) in [m3,M3]:
            if sign(interval) == 1.0:
                poss.append(self.scale_pitches[self.scale_pitches.index(self.ctp_notes[idx-1])+1])
            else:
                poss.append(self.scale_pitches[self.scale_pitches.index(self.ctp_notes[idx - 1]) - 1])
        if poss == []:
            return None
        return poss
    def _new_rules(self):
        indices = [1,3,5,7,9,11,13,15]
        print("hello")
        for idx in indices:
            harmonic_poss = self.get_harmonic_possibilities(self.expanded_cf[idx])
            dissonant_poss = self._get_dissonant_possibilities(idx)
            print("harmonic poss: ",harmonic_poss)
            print("dissonant poss: ",dissonant_poss)
            if dissonant_poss != None:
                print("Dissonance at idx: ",idx)
                self.ctp_notes[idx] = rm.choice(dissonant_poss)
            else:
                self.ctp_notes[idx] = rm.choice(harmonic_poss)
        print("ctp notes", self.ctp_notes)
        # Changing rhythm to account for proper ending..
        self.melody_rhythm.pop(-1)
        self.melody_rhythm.pop(-1)
        self.melody_rhythm.append(8)
        self.ctp_notes.pop(-1)