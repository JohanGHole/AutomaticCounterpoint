from music_module.constants import *
from counterpoint_module.third_species import *
from counterpoint_module.fourth_species import *
from counterpoint_module.first_species import *
from counterpoint_module.second_species import *
from counterpoint_module.fifth_species import *
from counterpoint_module.cf import *
import json
import matplotlib.pyplot as plt
def main():
    cont = True
    i = 0
    print("Automatic Species Generation")
    while cont:
        print(" ")
        key = input("key? :")
        scale_name = input("scale type? [major or minor]: ")
        species = input("Species? [first to fifth]: ")
        range_str = input("Voice range of cantus firmus? [bass, tenor, alto, soprano]: ")
        cf_range = RANGES[RANGES_NAMES[range_str]]
        if cf_range == BASS_RANGE:
            ctp_position = "y"
        elif cf_range == SOPRANO_RANGE:
            ctp_position = "n"
        else:
            ctp_position = input("above cantus firmus? [y/n]: ")
        if ctp_position[0].upper() == "Y":
            ctp_position = "above"
        else:
            ctp_position = "below"
        instrument = input("instrument? [Acoustic Grand Piano, Church Organ etc.]: ")
        name = "ctp"+str(i)
        mid_gen = Midi_Generator(key,scale_name,species,ctp_position = ctp_position,cf_range = cf_range)
        mid_gen.set_instrument(instrument)
        mid_gen.to_instrument()
        mid_gen.export_to_midi(name = "generated_midi/user_defined/"+species+"_species_"+name+".mid")
        print("midi successfully exported to "+"generated_midi/user_defined/"+species+"_species_"+name+".mid")
        cont_str = input("try again? [y/n]: ")
        if cont_str[0].upper() == "Y":
            cont = True
        else:
            cont = False
        i += 1



class Midi_Generator:
    instruments = ["Church Organ","Church Organ"]
    def __init__(self,key,scale_name,species, bar_length = 2,ctp_position = "above",cf_range = RANGES[TENOR],cf_notes = None,cf_rhythm = None):
        self.cf_range_name = RANGES.index(cf_range)
        self.species = species
        self.cf = Cantus_Firmus(key,scale_name,bar_length,cf_notes,cf_rhythm,start = 0, voice_range = cf_range)
        self.loaded_instruments = []
        if species == "first":
            self.ctp = FirstSpecies(self.cf,ctp_position = ctp_position)
        elif species == "second":
            self.ctp = SecondSpecies(self.cf,ctp_position = ctp_position)
        elif species == "third":
            self.ctp = ThirdSpecies(self.cf,ctp_position = ctp_position)
        elif species == "fourth":
            self.ctp = FourthSpecies(self.cf,ctp_position = ctp_position)
        elif species == "fifth":
            self.ctp = FifthSpecies(self.cf,ctp_position = ctp_position)
        self.ctp.generate_ctp()
        print(self.ctp.search_domain)
    def set_instrument(self,name):
        if isinstance(name,list):
            self.instruments = name
        else:
            self.instruments = [name]*2

    def to_instrument(self):
        cf_inst = pretty_midi.Instrument(program=pretty_midi.instrument_name_to_program(self.instruments[0]),name="cf")
        ctp_inst =pretty_midi.Instrument(program=pretty_midi.instrument_name_to_program(self.instruments[1]),name="ctp")
        self.ctp.melody.to_instrument(ctp_inst)
        self.loaded_instruments.append(ctp_inst)
        self.cf.to_instrument(cf_inst)
        self.loaded_instruments.append(cf_inst)

    def export_to_midi(self,tempo = 120, name = "generated_midi/user_defined/ctp.mid"):
        pm = pretty_midi.PrettyMIDI(initial_tempo= tempo)
        for inst in self.loaded_instruments:
            if inst != None:
                pm.instruments.append(inst)
        pm.write(name)




#large_test_four_voices(RANGES[TENOR])


main()

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
        ctp = Midi_Generator(key, scale, ctp_position=ctp_position, cf_range=RANGES[cf_range], bar_length=2)
        end = time()-start
        iteration_data["index"] = i
        iteration_data["error"] = ctp.ctp.error
        iteration_data["time"] = end
        iteration_data["penalties"] = ctp.penalty_list
        iteration_data["error_list"] = ctp.ctp.ctp_errors
        ctp.set_instrument(inst)
        ctp.to_instrument()
        ctp.export_to_midi(tempo=120, name="generated_midi/fifth_species/data2" + str(i) + ".mid")
        data.append(iteration_data)
    with open('data/fifth_species/data2.txt', 'w') as filehandle:
        json.dump(data, filehandle)
#result_generation()

def result_analysis():
    with open('data/fifth_species/data.txt', 'r') as filehandle:
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
    print("second most common error: ",most_common_error_list[1])
    print(f"precentage: ",(most_common_error[most_common_error_list[0]]/num_errors)*100)
    num_below_threshold = 0
    for e in errors:
        if e < THRESHOLD:
            num_below_threshold += 1
    print("precentage below threshold: ",num_below_threshold,"%")
    print("penalties: ",penalties[8])
    plt.plot(penalties[8])
    plt.ylabel('penalty')
    plt.xlabel("iteration nr")
    plt.show()
#result_analysis()