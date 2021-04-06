import pretty_midi
from music_module.constants import *

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

    def transpose(self, i):
        self.pitch += i

    def to_instrument(self, instrument):
        # adds the note to the given instrument
        if self.start == None or self.end == None:
            print("Error: no temporal information is given for the Note")
            pass
        note = pretty_midi.Note(velocity=self.velocity, pitch=self.pitch, start=self.start, end=self.end)
        instrument.notes.append(note)