from music_module.constants import *
from counterpoint_module.third_species import *
from counterpoint_module.fourth_species import *
from counterpoint_module.first_species import *
from counterpoint_module.second_species import *
from counterpoint_module.fifth_species import *
from counterpoint_module.cf import *
import json
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
        self.ctp = SecondSpecies(self.cf,ctp_position = ctp_position)#SecondSpecies(self.cf,ctp_position = "above")#FirstSpecies(self.cf,ctp_position = "above")
        self.penalty_list = self.ctp.generate_ctp()
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
    for i in range(100):
        ctp = Player(KEY_NAMES[i%len(KEY_NAMES)],"major",ctp_position = "above",cf_range = cf_range, bar_length = 2)
        ctp.set_instrument(inst)
        ctp.to_instrument()
        ctp.export_to_midi(tempo = 120, name = "generated_midi/first_species/others"+str(i+1)+".mid")


#large_test_four_voices(RANGES[TENOR])
subject = [60, 60, 67, 67, 69, 69, 67, 65, 65, 64, 64, 62, 62, 60, 60, 67, 69, 67, 65, 64, 62, 60]
subject_rhythm = [(4, 4), (4, 4), (4, 4), (8,), (4, 4), (4, 4), (4, 4), (8,), (8,), (8,), (8,), (8,), (8,), (8,),
                      (8,), (8,)]

""" What do the test need?
TODO:
Generate 100 counterpoints of each species with randomized scale_type, counterpoint position (below or above) and vocal range """

def result_generation():
    inst = ["Acoustic Grand Piano"] * 4
    data = []
    for i in range(100):
        iteration_data = {}
        key = rm.choice(KEY_NAMES)
        scale = rm.choice(["major","minor"])
        cf_range = rm.choice([BASS, TENOR, ALTO, SOPRANO])
        if cf_range == SOPRANO:
            ctp_position = "below"
        elif cf_range == BASS:
            ctp_position = "above"
        else:
            ctp_position = rm.choice(["above","below"])
        start = time()
        ctp = Player(key, scale, ctp_position=ctp_position, cf_range=RANGES[cf_range], bar_length=2)
        end = time()-start
        iteration_data["index"] = i
        iteration_data["error"] = ctp.ctp.error
        iteration_data["time"] = end
        iteration_data["penalties"] = ctp.penalty_list
        iteration_data["error_list"] = ctp.ctp.ctp_errors
        ctp.set_instrument(inst)
        ctp.to_instrument()
        ctp.export_to_midi(tempo=120, name="generated_midi/second_species/test" + str(i) + ".mid")
        data.append(iteration_data)
    with open('data/second_species/data.txt', 'w') as filehandle:
        json.dump(data, filehandle)
#result_generation()

def result_analysis():
    with open('data/second_species/data.txt', 'r') as filehandle:
        data = json.load(filehandle)
    THRESHOLD = 100
    errors = []
    penalties = []
    errors_list = []
    time_list = []
    zero_errors = []
    for i in range(len(data)):
        errors.append(data[i]["error"])
        penalties.append(data[i]["penalties"])
        errors_list.append(data[i]["error_list"])
        if errors[i] == 0:
            zero_errors.append(i)
        time_list.append(data[i]["time"])
    print("average time: ",sum(time_list)/len(data))
    print("average error: ",sum(errors)/len(data))
    print("worst case :",max(errors), "at index ",errors.index(max(errors)), "with errors ",errors_list[errors.index(max(errors))], "and comp time ",time_list[errors.index(max(errors))])
    print("zero errors: ",zero_errors)
    most_common_error = {}
    for i in errors_list:
        for e in i:
            if e not in most_common_error.keys():
                most_common_error[e] = 1
            else:
                most_common_error[e] += 1
    most_common_error = dict(sorted(most_common_error.items(),reverse=True, key=lambda item: item[1]))
    most_common_error_list = list(most_common_error.keys())
    num_errors = 0
    for key in most_common_error:
        num_errors += most_common_error[key]
    print("most common error: ",most_common_error_list[0])
    print(f"precentage: ",(most_common_error[most_common_error_list[0]]/num_errors)*100)
    num_below_threshold = 0
    for e in errors:
        if e < THRESHOLD:
            num_below_threshold += 1
    print("precentage below threshold: ",num_below_threshold,"%")
result_analysis()