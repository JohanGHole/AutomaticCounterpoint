import pretty_midi
import IPython.display
import numpy as np
# For plotting
import mir_eval.display
import librosa.display
import matplotlib.pyplot as plt
import pypianoroll
# For putting audio in the notebook
import IPython.display
midi_data = pretty_midi.PrettyMIDI('midi_folder\WTC1\wtc1f01.mid')
print(midi_data.estimate_tempo())
total_velocity = sum(sum(midi_data.get_chroma()))
print([sum(semitone)/total_velocity for semitone in midi_data.get_chroma()])
for instrument in midi_data.instruments:
    # Don't want to shift drum notes
    if not instrument.is_drum:
        for note in instrument.notes:
            note.pitch += 5
# Synthesize the resulting MIDI data using sine waves
audio_data = midi_data.fluidsynth(fs=16000)
IPython.display.Audio(midi_data.fluidsynth(fs=16000),rate=16000)

def plot_piano_roll(pm, start_pitch, end_pitch, fs=100):
    # Use librosa's specshow function for displaying the piano roll
    librosa.display.specshow(pm.get_piano_roll(fs)[start_pitch:end_pitch],
                             hop_length=1, sr=fs, x_axis='time', y_axis='cqt_note',
                             fmin=pretty_midi.note_number_to_hz(start_pitch))
midi_data.write('out.midi')
plt.figure(figsize=(12,4))
plot_piano_roll(midi_data,40,96,fs=100)
plt.show()
# Note the blurry section between 1.5s and 2.3s - that's the pitch bending up!
print(61 % 12)