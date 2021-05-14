""" SEARCH ALGORITHM """
import math
import itertools
from constraints_module.constraints import Constraints
def _get_indices(cf_notes,idx, n_window):
    s_w = []
    for i in range(n_window):
        if idx + i < len(cf_notes):
            s_w.append(idx + i)
        else:
            s_w.append(len(cf_notes) - 1 - i)
    s_w.sort()
    return [s_w[0],s_w[-1]]

def _path_search(species,ctp_draft,cf_notes,scale_pitches,ctp_position,error,search_window,poss,protected_indices):
    paths = []
    if protected_indices != []:
        for idx in protected_indices:
            if idx in range(search_window[0],search_window[1]+1):
                return ctp_draft, error
    for i in itertools.product(*poss[search_window[0]:search_window[1]+1]):
        paths.append(list(i))
    ctp_draft[search_window[0]:search_window[1]+1] = paths[0]
    best_ctp = ctp_draft.copy()
    best_local_error = math.inf
    best_error_list = []
    for path in paths:
        ctp_draft[search_window[0]:search_window[1] + 1] = path
        enforced_constrains = Constraints(species,ctp_draft,cf_notes,scale_pitches,ctp_position)
        local_error = enforced_constrains.get_penalty()
        ctp_errors = enforced_constrains.get_errors()
        if  local_error < best_local_error:
            best_ctp = ctp_draft.copy()
            best_local_error = local_error
            best_error_list = ctp_errors
    return best_ctp.copy(), best_local_error, best_error_list

def search(species,ctp_draft,cf_notes,poss, scale_pitches,ctp_position, MAX_SEARCH_WIDTH = 3, ERROR_THRESHOLD = 50):
    error = math.inf
    best_scan_error = math.inf
    j = 1
    protected_indices = []
    best_ctp = ctp_draft.copy()
    best_error_list = []
    while error >= ERROR_THRESHOLD and j <= MAX_SEARCH_WIDTH:
        error_window = math.inf
        for i in range(len(ctp_draft)):
            window_n = _get_indices(cf_notes,i,j)
            ctp_draft, error, list_of_errors = _path_search(species,best_ctp.copy(),cf_notes,scale_pitches,ctp_position,error,window_n,poss,protected_indices)
            if i == 0:
                error_window = error
            if error < best_scan_error:
                best_ctp = ctp_draft.copy()
                best_scan_error = error
                best_error_list = list_of_errors
                if error < ERROR_THRESHOLD:
                    return best_scan_error, best_ctp, best_error_list
        if error_window <= best_scan_error:
            # No improvement, expand the window
            j += 1
    return best_scan_error,best_ctp, best_error_list