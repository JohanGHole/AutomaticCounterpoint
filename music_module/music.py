"""
Objects related to the musical building blocks
Includes helper functions for easy testing.
"""
import pretty_midi
from music_module.constants import *
import math
import random as rm


def export_to_midi(instrument, tempo=120.0, pm=None, name="test.mid"):
    name = "generated_midi/"+name
    if pm == None:
        pm = pretty_midi.PrettyMIDI(initial_tempo=tempo)
    else:
        pm = pm
    pm.instruments.append(instrument)
    pm.write(name)


class Note:
    """ Note object to handle note and octave information

        Attributes:
            pitch  [int / str]    -- corresponding MIDI pitch or pitch name as string
            start    [int]        -- start time for the note
            end      [int]        -- end time
            velocity [int]        -- the strength of which the note should be played
        """

    def __init__(self, pitch, start=None, end=None, velocity=100):
        if str(pitch) == pitch:
            self.pitch = pretty_midi.note_name_to_number(pitch)
        else:
            self.pitch = pitch
        self.start = start
        self.end = end
        self.velocity = velocity

    def copy(self):
        return Note(self.pitch, self.start, self.end, self.velocity)

    def get_pitch(self):
        return self.pitch

    def set_time(self, start, duration):
        self.start = start
        self.end = start + duration

    def get_duration(self):
        if self.start == None or self.end == None:
            return None
        else:
            return self.end - self.start

    def transpose(self, i, inPlace = False):
        if inPlace:
            self.pitch += i
        else:
            return Note(self.pitch+i,self.start,self.end,self.velocity)

    def to_instrument(self, instrument):
        # adds the note to the given instrument
        if self.start == None or self.end == None:
            print("Error: no temporal information is given for the Note")
            pass
        note = pretty_midi.Note(velocity=self.velocity, pitch=self.pitch, start=self.start, end=self.end)
        instrument.notes.append(note)

    """ USED IN EARLY TESTING """
    def to_midi(self, tempo=120, name="music_module/test.mid", program=0, instrument=None, pm=None):
        if instrument == None:
            inst = pretty_midi.Instrument(program=program, is_drum=False)
        else:
            inst = instrument
        self.to_instrument(inst)
        if pm == None:
            pm = pretty_midi.PrettyMIDI(initial_tempo=tempo)
        pm.instruments.append(inst)
        pm.write(name)


class Interval:
    perfect_intervals = [Unison, P5, Octave]
    dissonant_intervals = [m2, M2, P4, m7, M7, Tritone]
    consonant_intervals = [m3, M3, P5, m6, M6, Octave]
    melodic_consonant_intervals = [m2,M2,m3, M3, P4, P5, m6, M6, Octave]

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
    def is_melodic_consonant(self):
        if self.interval in self.melodic_consonant_intervals:
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


class Scale:
    """
    The scale class manages scale object. This include the construction of scales included in the NAMED_SCALE dict.
    the scale is a list of all possible notes in the given scale across the entire piano. This means that the root note
    is not nessecarily the lowest note.
    """

    def __init__(self, key, scale, scale_range=None):
        if key[0].upper() not in (KEY_NAMES_SHARP or KEY_NAMES):
            print("Error, key name not valid. Try on the format 'C' or 'Db' ")
            pass
        if key in ["A", "A#", "B", "Bb"]:
            oct = 0
        else:
            oct = 1
        self.root = Note(key + str(oct))  # sets the root of the scale in valid string format
        self.key = key
        self.scale_type = scale
        if isinstance(scale, str):
            scale = Scale.intervals_from_name(scale)
        elif isinstance(scale, Scale):
            scale = scale.intervals
        self.intervals = tuple(scale)
        self.scale = self.build_scale()
        self.scale_pitches = self.get_scale_pitches()
        if scale_range != None:
            self.limit_range(scale_range)

    @classmethod
    def intervals_from_name(self, scale_name):
        global NAMED_SCALES
        scale_name = scale_name.lower()

        # supporting alternative formatting..
        for text in ['scale', 'mode']:
            scale_name = scale_name.replace(text, '')
        for text in [" ", "-"]:
            scale_name = scale_name.replace(text, "_")
        return NAMED_SCALES[scale_name]

    def build_scale(self):
        start_pitch = self.root.get_pitch()
        scale_len = len(self.intervals)
        highest_possible_pitch = pretty_midi.note_name_to_number("C8")
        lowest_possible_pitch = pretty_midi.note_name_to_number("A0")
        j = 0
        scale = []
        pitch = start_pitch
        # adds all possible values above the root pitch
        while pitch <= highest_possible_pitch:
            scale.append(Note(pitch))
            pitch = scale[j].get_pitch() + self.intervals[j % scale_len]
            j += 1
        # adds all possible values under the root pitch
        j = scale_len - 1
        pitch = start_pitch - self.intervals[j % scale_len]
        while pitch >= lowest_possible_pitch:
            scale.insert(0, Note(pitch))
            j -= 1
            pitch = pitch - self.intervals[j % scale_len]
        return scale

    def get_scale_pitches(self):
        scale_pitches = []
        for notes in self.scale:
            scale_pitches.append(notes.get_pitch())
        return scale_pitches

    def get_scale_range(self, scale_range):
        """
              :param scale_range: [int] list of note pitches in the range to be returned
              :return: the scale limited to the given range
              """
        scale_pitches = []
        for notes in scale_range:
            if notes in self.scale_pitches:
                scale_pitches.append(notes)
        return scale_pitches

    def limit_range(self, scale_range):
        scale = []
        for notes in scale_range:
            if notes in self.scale_pitches:
                scale.append(Note(notes))
        self.scale = scale

    def set_time(self, duration):
        t = 0
        for notes in self.scale:
            notes.set_time(t, duration)
            t += duration

    def to_instrument(self, instrument):
        for notes in self.scale:
            notes.to_instrument(instrument)


class Melody:
    def __init__(self, key, scale, bar_length, melody_notes=None, melody_rhythm = 8, start=0, voice_range = None):
        self.key = key
        self.scale_name = scale
        self.voice_range = voice_range
        self.scale = Scale(key, scale, voice_range)
        self.scale_pitches = self.scale.get_scale_pitches()
        self.note_resolution = 8
        self.start = start
        self.bar_length = float(bar_length)
        if melody_notes == None:
            num_bars = rm.randint(8, 12)
            mel = [60 for i in range(num_bars)]
            self.melody = mel
        else:
            self.melody = melody_notes
        if isinstance(melody_rhythm, int):
            self.melody_rhythm = [melody_rhythm for elem in self.melody]
        elif isinstance(melody_rhythm, list):
            self.melody_rhythm = melody_rhythm




    def get_end_time(self):
        t = self.start
        for elem in self.melody_rhythm:
            t += elem
        return t*self.bar_length / float(self.note_resolution)
        "ANALYSIS AND AUGMENTATION"

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
            return Melody(self.key, self.scale_name, self.bar_length, melody_notes=inverted_melody, melody_rhythm=self.melody_rhythm,
                          start=self.start, voice_range=self.voice_range)

    def retrograde(self, in_place=False):
        timeScale = self.melody_rhythm
        retrograded = []
        retrograded_timeScale = []
        for i in range(len(self.melody) - 1, -1, -1):
            retrograded.append(self.melody[i])
            retrograded_timeScale.append(timeScale[i])
        if in_place:
            self.melody = retrograded
            self.melody_rhythm = retrograded_timeScale
        else:
            return Melody(self.key, self.scale_name, self.bar_length, melody_notes=retrograded,
                          melody_rhythm=retrograded_timeScale,
                          start=self.start, voice_range=self.voice_range)

    """ MIDI SUPPORT """

    def to_instrument(self, instrument, time=None, start = 0):
        if time == None and start == None:
            t = self.start
            time = self.melody_rhythm
            i = 0
            for pitch in self.melody:
                dur = float(time[i]*self.bar_length / float(self.note_resolution))
                note = Note(pitch, start=t, end=t + dur)
                note.to_instrument(instrument)
                t += dur
                i += 1
        elif isinstance(time, int):
            t = start
            for pitch in self.melody:
                dur = float(time*self.bar_length / float(self.note_resolution))
                note = Note(pitch, start=t, end=t + dur)
                note.to_instrument(instrument)
                t += dur
        elif isinstance(time, list) and len(time) == len(self.melody):
            t = start
            for i in range(len(self.melody)):
                dur = float(time[i] * self.bar_length / float(self.note_resolution))
                if self.melody[i] != -1:

                    note = Note(self.melody[i], start=t, end=t + dur)
                    note.to_instrument(instrument)
                t += dur
