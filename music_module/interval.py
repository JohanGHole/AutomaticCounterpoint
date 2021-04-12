from music_module.note import *

class Interval:
    perfect_intervals = [Unison, P5, Octave]
    dissonant_intervals = [m2, M2, m7, M7, Tritone]
    consonant_intervals = [m3, M3, P4, P5, m6, M6, Octave]

    def __init__(self, arg1=None, arg2=None, arg3=None):
        self.note1 = arg1
        self.note2 = arg2
        self.interval = arg3
        if isinstance(arg1, Note) and isinstance(arg2, int):
            self.note1 = arg1
            self.interval = arg2
            self.note2 = self.note1.copy()
            self.note2.transpose(self.interval)

        elif isinstance(arg1, int):
            self.interval = arg1

        elif isinstance(arg1, Note) and isinstance(arg2, Note):
            self.note2 = arg2
            self.note1 = arg1
            self.interval = self.note2.pitch - self.note1.pitch

        elif arg3 == None and not isinstance(arg1, int):
            self.interval = self.note2.pitch - self.note1.pitch
        self.name = self.get_pretty_name()

    def invert(self):
        return Interval(self.note1, -self.interval)

    def to_instrument(self, instrument):
        self.note1.to_instrument(instrument)
        self.note2.to_instrument(instrument)

    def get_pretty_name(self):
        i = self.interval
        pretty_name = ""
        if i == 0:
            pretty_name = "unison"
        if i == m2:
            pretty_name = "minor second"
        elif i == M2:
            pretty_name = "major second"
        elif i == m3:
            pretty_name = "minor third"
        elif i == M3:
            pretty_name = "major third"
        elif i == P4:
            pretty_name = "perfect fourth"
        elif i == d5:
            pretty_name = "diminished fifth"
        elif i == P5:
            pretty_name = "perfect fifth"
        elif i == m6:
            pretty_name = "augmented fifth"
        elif i == M6:
            pretty_name = "major sixth"
        elif i == m7:
            pretty_name = "minor seventh"
        elif i == M7:
            pretty_name = "major seventh"
        elif i == Octave:
            pretty_name = "octave"
        return pretty_name

    def is_dissonant(self):
        if self.interval in self.dissonant_intervals:
            return True
        else:
            return False

    def is_consonant(self):
        if self.interval in self.consonant_intervals:
            return True
        else:
            return False

    def is_perfect(self):
        if self.interval in self.perfect_intervals:
            return True
        else:
            return False
