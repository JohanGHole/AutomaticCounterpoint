ctp_draft = [62,62,63,67,60,67,60]

def _is_motivic_repetitions(ctp_draft):
    for i in range(len(ctp_draft)-3):
        print(ctp_draft[i:i+2])
        print(ctp_draft[i+2:i+4])
        if ctp_draft[i:i+2] == ctp_draft[i+2:i+4]:
            return True
    return False
print(_is_motivic_repetitions(ctp_draft))

ctp_draft = [67,69,76,67,69,69,72,67,69,60]
cf = [60,60,60,60,60,60,60,60,57,60]

def _is_parallel_perfects_on_downbeats(ctp_draft, upper_voice, lower_voice):
    db = [0,2,4,6,8]
    for i in range(len(db) - 1):
        interval1 = upper_voice[db[i]] - lower_voice[db[i]]
        interval2 = upper_voice[db[i + 1]] - lower_voice[db[i + 1]]
        if interval1 == interval2 and interval1 in [7,12]:
            # consecutive perfects on downbeats
            if upper_voice[db[i + 1]] - upper_voice[db[i]] == lower_voice[db[i + 1]] - lower_voice[db[i]]:
                # consecutive and parallel
                if ctp_draft[db[i]] - ctp_draft[db[i] + 1] > 4:
                    return False
                else:
                    return True
            return False

    return False

rhythm = [4,6,2,2,2,2,2,6,2,2,2,2,2,2,2,2,2,8,4,4]
test = [[8]]*8

print("this is a tuple: ",[(8,4)]*8)
print(sum((8,4)))
def cf_index(ctp_index):
    # Inputs the cf_index and returns
    print("ctp_index..",sum(rhythm[:ctp_index]))
    return int((sum(rhythm[:ctp_index+1]) / 8))

print([(8,8)]*4)
print(2%2)
