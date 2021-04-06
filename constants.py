# Names and ranges
KEY_NAMES = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
KEY_NAMES_SHARP = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
SHARPS_IDX = [1, 3, 6, 8, 10]

BASS_RANGE = [40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51,
              52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64]

TENOR_RANGE = [48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59,
               60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72]

ALTO_RANGE = [53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64,
              65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77]

SOPRANO_RANGE = [60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71,
                 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84]
BASS = 0
TENOR = 1
ALTO = 2
SOPRANO = 3
RANGES = [[40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51,
           52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64],
          [48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59,
           60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72],
          [53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64,
           65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77],
          [60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71,
           72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83, 84]
          ]
# intervals
P1 = C = Tonic = Unison = 0
m2 = Db = 1
M2 = D = 2
m3 = Eb = 3
M3 = E = 4
P4 = F = 5
d5 = Gb = Tritone = 6
P5 = G = 7
m6 = Ab = 8
M6 = A = 9
m7 = Bb = 10
M7 = B = 11
P8 = Octave = 12

NAMED_SCALES = {
    "major": (2, 2, 1, 2, 2, 2, 1),
    "minor": (2, 1, 2, 2, 1, 2, 2),
    "melodic_minor": (2, 1, 2, 2, 2, 2, 1),
    "harmonic_minor": (2, 1, 2, 2, 1, 3, 1),
    "chromatic": (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
}
