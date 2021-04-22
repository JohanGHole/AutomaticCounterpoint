from music_module.scale import *
import random as rm
class Melody:
    def __init__(self, key, scale, bar_length, melody_notes=None, melody_rhythm = None, start=0, vocal_range=None):
        self.key = key
        self.scale_name = scale
        self.vocal_range = vocal_range
        self.scale = Scale(key, scale, vocal_range)
        self.scale_pitches = self.scale.get_scale_pitches()
        self.note_resolution = 8
        self.start = start
        self.bar_length = bar_length
        self.melody = None
        if melody_notes != None:
            self.melody = melody_notes
        else:
            self.generate_melody()
        if isinstance(melody_rhythm, int):
            self.time = [melody_rhythm for elem in self.melody]
        elif isinstance(melody_rhythm, list):
            self.time = melody_rhythm

    @classmethod
    def generate_melody(self):
        length_in_bars = rm.randint(4, 8)
        mel = [60 for elem in length_in_bars]
        self.melody = mel

    def get_end_time(self):
        t = self.start
        for elem in self.time:
            t += elem
        return t

    def get_note_durations(self):
        dur = []
        for notes in self.melody:
            dur.append(notes.get_duration())
        return dur

    def diatonic_inversion(self, in_place=False):
        notes = self.melody
        inverted_melody = [notes[0]]
        # Might have to change the range for the new melody. It can easily go out of range given the limited voice range
        for i in range(len(notes) - 1):
            interval = self.scale_pitches.index(notes[i + 1]) - self.scale_pitches.index(notes[i])
            idx = self.scale_pitches.index(inverted_melody[i]) - interval
            if idx < 0:
                print("ERROR: inversion out of bounds")
                pass
            new_note = self.scale_pitches[idx]
            inverted_melody.append(new_note)

        if in_place:
            self.melody = inverted_melody
        else:
            return Melody(self.key, self.scale_name, self.bar_length, melody_notes=inverted_melody, time=self.time,
                          start=self.start, vocal_range=self.vocal_range)

    def retrograde(self, in_place=False):
        timeScale = self.time
        retrograded = []
        retrograded_timeScale = []
        for i in range(len(self.melody) - 1, -1, -1):
            retrograded.append(self.melody[i])
            retrograded_timeScale.append(timeScale[i])
        if in_place:
            self.melody = retrograded
            self.time = retrograded_timeScale
        else:
            return Melody(self.key, self.scale_name, self.bar_length, melody_notes=retrograded,
                          time=retrograded_timeScale,
                          start=self.start, vocal_range=self.vocal_range)

    """ MIDI SUPPORT """

    def to_instrument(self, instrument, time=None, start=None):
        if time == None and start == None:
            t = self.start
            time = self.time
            i = 0
            for pitch in self.melody:
                note = Note(pitch, start=t, end=t + time[i])
                note.to_instrument(instrument)
                t += time[i]
                i += 1
        elif isinstance(time, float) or isinstance(time, int):
            t = start
            for pitch in self.melody:
                note = Note(pitch, start=t, end=t + time)
                note.to_instrument(instrument)
                t += time
        elif isinstance(time, list) and len(time) == len(self.melody):
            t = start
            for i in range(len(self.melody)):
                note = Note(self.melody[i], start=t, end=t + time[i])
                note.to_instrument(instrument)
                t += time[i]