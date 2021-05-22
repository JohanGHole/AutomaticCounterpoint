from music_module.constants import *
from counterpoint_module.third_species import *
from counterpoint_module.fourth_species import *
from counterpoint_module.first_species import *
from counterpoint_module.second_species import *
from counterpoint_module.fifth_species import *
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
    instruments = ["cello","viola","viola","violin"]
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
        self.ctp = FifthSpecies(self.cf,ctp_position = ctp_position)#SecondSpecies(self.cf,ctp_position = "above")#FirstSpecies(self.cf,ctp_position = "above")
        self.ctp.generate_ctp()
    def set_instrument(self,name):
        self.instruments = name
    def to_instrument(self):
        cf_inst = pretty_midi.Instrument(program=pretty_midi.instrument_name_to_program(self.instruments[0]),name="cf")
        ctp_inst =pretty_midi.Instrument(program=pretty_midi.instrument_name_to_program(self.instruments[1]),name="ctp")
        self.ctp.ctp.to_instrument(ctp_inst)
        self.loaded_instruments.append(ctp_inst)
        self.cf.to_instrument(cf_inst)
        self.loaded_instruments.append(cf_inst)
    def export_to_midi(self,tempo = 120, name = "generated_midi/first_species/ctp1.mid"):
        pm = pretty_midi.PrettyMIDI(initial_tempo= tempo)
        for inst in self.loaded_instruments:
            if inst != None:
                pm.instruments.append(inst)
        pm.write(name)

def large_test_four_voices(cf_range):
    inst = ["church organ"]*4
    for i in range(10):
        ctp = Player(KEY_NAMES[i%len(KEY_NAMES)],"major",ctp_position = "above",cf_range = cf_range, bar_length = 2)
        ctp.set_instrument(inst)
        ctp.to_instrument()
        ctp.export_to_midi(tempo = 120, name = "generated_midi/fifth_species/test"+str(i+1)+".mid")


large_test_four_voices(RANGES[TENOR])
subject = [60, 60, 67, 67, 69, 69, 67, 65, 65, 64, 64, 62, 62, 60, 60, 67, 69, 67, 65, 64, 62, 60]
subject_rhythm = [(4, 4), (4, 4), (4, 4), (8,), (4, 4), (4, 4), (4, 4), (8,), (8,), (8,), (8,), (8,), (8,), (8,),
                      (8,), (8,)]
