from music_module.interval import *

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