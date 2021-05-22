""" SEARCH ALGORITHM """
import math
import itertools
from constraints_module.constraints import Constraints
import time as t
import random as rm
def _get_indices(ctp_len,idx, n_window):
    s_w = []
    for i in range(n_window):
        if idx + i < ctp_len:
            s_w.append(idx + i)
        else:
            s_w.append(ctp_len - 1 - i)
    s_w.sort()
    return [s_w[0],s_w[-1]]

def _path_search(ctp,search_window):
    paths = []
    ctp_draft = ctp.ctp.melody.copy()
    poss = ctp.search_domain
    for i in itertools.product(*poss[search_window[0]:search_window[1]+1]):
        paths.append(list(i))
    ctp_draft[search_window[0]:search_window[1]+1] = paths[0]
    best_ctp = ctp_draft.copy()
    best_local_error = math.inf
    best_error_list = []
    for path in paths:
        ctp_draft[search_window[0]:search_window[1] + 1] = path
        ctp.ctp.set_melody(ctp_draft)
        enforced_constrains = Constraints(ctp)
        local_error = enforced_constrains.get_penalty()
        ctp_errors = enforced_constrains.get_errors()
        weighted_indices = enforced_constrains.get_weighted_indices()
        if  local_error < best_local_error:
            best_ctp = ctp_draft.copy()
            ctp.ctp.set_melody(best_ctp)
            best_local_error = local_error
            best_error_list = ctp_errors
    return best_ctp.copy(), best_local_error, best_error_list

def search(ctp):
    error = math.inf
    best_scan_error = math.inf
    j = 1
    best_ctp = ctp.ctp.melody.copy()
    best_error_list = []
    while error >= ctp.ERROR_THRESHOLD and j <= ctp.MAX_SEARCH_WIDTH:
        error_window = math.inf
        for i in range(len(ctp.ctp.melody)):
            window_n = _get_indices(len(ctp.ctp.melody),i,2)
            ctp_draft, error, list_of_errors = _path_search(ctp,window_n)
            if i == 0:
                error_window = error
            if error < best_scan_error:
                best_ctp = ctp_draft.copy()
                ctp.ctp.set_melody(best_ctp)
                best_scan_error = error
                best_error_list = list_of_errors
                if error < ctp.ERROR_THRESHOLD:
                    return best_scan_error, best_ctp, best_error_list

            """ steps_since_improvement += 1
            if steps_since_improvement >= len(ctp.ctp.melody):
                ctp.ctp.set_melody(ctp.randomize_ctp_melody())
                steps_since_improvement = 0
                j = 1"""
        ctp.ctp.set_melody(best_ctp)
        if error_window >= best_scan_error:
            j += 1
    return best_scan_error,best_ctp, best_error_list

def brute_force(ctp):
    penalty = math.inf
    errors = []
    while penalty > ctp.ERROR_THRESHOLD:
        ctp.ctp.set_melody(ctp.randomize_ctp_melody())
        enforced_constrains = Constraints(ctp)
        local_error = enforced_constrains.get_penalty()
        ctp_errors = enforced_constrains.get_errors()
        penalty = local_error
        errors = ctp_errors
    return penalty, ctp.ctp.melody,errors
def best_first_search(ctp,weighted_idx,tabu_list):
    search_domain = ctp.search_domain
    search_ctp = ctp.ctp.melody.copy()
    best_global_ctp = search_ctp.copy()
    best_global_error = math.inf
    best_global_error_list = []
    best_global_weighted_indices = []
    if isinstance(weighted_idx,list):
        idx = weighted_idx
    else:
        idx = list(weighted_idx.keys())
    for i in idx:
        best_note = search_domain[i][0]
        local_error = math.inf
        local_error_list = []
        local_weighted_indices = []
        for j in range(len(search_domain[i])):
            search_ctp[i] = search_domain[i][j]
            ctp.ctp.set_melody(search_ctp.copy())
            constrained = Constraints(ctp)
            error = constrained.get_penalty()
            error_list = constrained.get_errors()
            weighted_indices = constrained.get_weighted_indices()
            if error <= local_error and search_domain[i][j] not in tabu_list[i]:
                best_note = search_domain[i][j]
                local_error = error
                local_error_list = error_list
                local_weighted_indices = weighted_indices
        search_ctp[i] = best_note
        if local_error < best_global_error:
            best_global_ctp = search_ctp.copy()
            best_global_error = local_error
            best_global_error_list = local_error_list
            best_global_weighted_indices = local_weighted_indices
    return best_global_error, best_global_ctp, best_global_error_list,best_global_weighted_indices

def improved_search(ctp):
    """ How? """
    start_time = t.time()
    penalty = math.inf
    elapsed_time = t.time()-start_time
    best_ctp = ctp.ctp.melody.copy()
    lowest_error = []
    lowest_penalty = math.inf
    weighted_idx = [i for i in range(len(best_ctp))]
    prev_penalty = penalty
    searches = 1
    tabu_list = [[]]*len(best_ctp)
    randomize_idx = 1
    while penalty > ctp.ERROR_THRESHOLD and elapsed_time < ctp.MAX_SEARCH_TIME:
        penalty, ctp_notes, error_list,weighted_idx = best_first_search(ctp,weighted_idx,tabu_list)
        if penalty == prev_penalty:
            weighted_idx = list(weighted_idx.keys())
            for i in range(randomize_idx):
                ctp_notes[weighted_idx[i]] = rm.choice(ctp.search_domain[weighted_idx[i]])
            rm.shuffle(weighted_idx)
            ctp.ctp.set_melody(ctp_notes)
            if randomize_idx != len(best_ctp)-1:
                randomize_idx += 1
        if penalty < lowest_penalty:
            randomize_idx = 1
            best_ctp = ctp_notes
            ctp.ctp.set_melody(best_ctp)
            lowest_penalty = penalty
            lowest_error = error_list
            weighted_idx = weighted_idx
        elapsed_time = t.time()-start_time
        prev_penalty = penalty
        searches += 1
    return lowest_penalty, best_ctp,lowest_error