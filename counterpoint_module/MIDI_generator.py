from music_module.constants import *
from counterpoint_module.third_species import *
from counterpoint_module.fourth_species import *
from counterpoint_module.cf import *
class Player:
    # Max four instruments
    # String quartet or organ
    """
    41 Violin
    42 Viola
    43 Cello
    44 Contrabass
    """
    instruments = ["contrabass","cello","viola","violin"]
    def __init__(self,key,scale_name, bar_length = 1,ctp_position = "above",cf_range = RANGES[TENOR],cf_notes = None,cf_rhythm = None):
        self.key = key
        self.scale_name = scale_name
        self.cf_range = cf_range
        self.cf_range_name = RANGES.index(self.cf_range)
        self.bar_length = bar_length
        self.cf = Cantus_Firmus(key,scale_name,bar_length,cf_notes,cf_rhythm,start = 0, voice_range = cf_range)
        self.cf.generate_cf()
        self.voices = [None, None, None, None]
        self.loaded_instruments = [None, None, None, None]
        self.voices[self.cf_range_name] = self.cf
        ctp = ThirdSpecies(self.cf,ctp_position = ctp_position)#SecondSpecies(self.cf,ctp_position = "above")#FirstSpecies(self.cf,ctp_position = "above")
        ctp.generate_ctp()
        ctp.construct_ctp_melody(0)
        self.voices[self.cf_range_name + 1] = ctp.ctp_melody

    def set_instrument(self,name):
        self.instruments = name

    def to_instrument(self):
        i = 0
        for melodies in self.voices:
            if melodies != None:
                if i == 0:
                    inst = pretty_midi.Instrument(program=pretty_midi.instrument_name_to_program(self.instruments[i]),
                                                  is_drum=False, name="Bass")
                    self.voices[i].to_instrument(inst, time=self.voices[i].melody_rhythm, start=0)
                    self.loaded_instruments[i] = inst
                elif i == 1:
                    inst = pretty_midi.Instrument(program=pretty_midi.instrument_name_to_program(self.instruments[i]),
                                                  is_drum=False, name="Tenor")
                    self.voices[i].to_instrument(inst,time=self.voices[i].melody_rhythm, start=0)
                    self.loaded_instruments[i] = inst
                elif i == 2:
                    inst = pretty_midi.Instrument(program=pretty_midi.instrument_name_to_program(self.instruments[i]),
                                                  is_drum=False, name="Alto")
                    self.voices[i].to_instrument(inst,time=self.voices[i].melody_rhythm, start=0)
                    self.loaded_instruments[i] = inst
                elif i == 3:
                    inst = pretty_midi.Instrument(program=pretty_midi.instrument_name_to_program(self.instruments[i]),
                                                  is_drum=False, name="Soprano")
                    self.voices[i].to_instrument(inst, time=self.voices[i].melody_rhythm, start=0)
                    self.loaded_instruments[i] = inst
            i += 1

    def export_to_midi(self,tempo = 120, name = "generated_midi/first_species/ctp1.mid"):
        pm = pretty_midi.PrettyMIDI(initial_tempo= tempo)
        for inst in self.loaded_instruments:
            if inst != None:
                pm.instruments.append(inst)
        pm.write(name)

def large_test_four_voices(cf_range):
    inst = ["Electric Piano 1"]*4
    for i in range(10):
        ctp = Player(KEY_NAMES[i%len(KEY_NAMES)],"major",ctp_position = "above",cf_range = cf_range, bar_length = 2)
        ctp.set_instrument(inst)
        ctp.to_instrument()
        ctp.export_to_midi(tempo = 120, name = "generated_midi/third_species/test"+str(i)+".mid")

large_test_four_voices(RANGES[ALTO])