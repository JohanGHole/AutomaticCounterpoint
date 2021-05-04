

l = [60,62,64,65,76,60]
print(l[1:-1])
test = {}
test[(60,67)] = 500
test = [60,67]

ctp_notes = [60,60,60,60,60,60,60]
def _get_indices(ctp_notes, idx, n_window):
    s_w = []
    for i in range(n_window):
        if idx + i < len(ctp_notes):
            s_w.append(idx + i)
        else:
            s_w.append(len(ctp_notes)-1-i)
    s_w.sort()
    return s_w
search_window = _get_indices(ctp_notes,0,3)
print(search_window[1:])

poss = [[10,15],[10,15,20,25,30],[60,30,15,20]]
ctp_draft = [10,15,30]
paths = []
search_window = [0,2]
import itertools
for i in itertools.product(*poss):
    paths.append(i)
def recursive_search(poss,search_window):
    paths = []
    for i in itertools.product(*poss[search_window[0]:search_window[1]+1]):
        paths.append(list(i))
    best_path = paths[0]
    for path in paths:
        if sum(path) < sum(best_path):
            best_path = path

    return best_path, sum(best_path)

print(recursive_search(poss,search_window))
ctp_draft = [60,62,64,65,67,69,71,72]
poss = [[60, 67, 72], [67, 71, 72, 76, 79], [69, 72, 74, 77, 81], [67, 71, 72, 76, 79], [71, 74, 76, 79, 83], [69, 72, 74, 77, 81], [71, 74, 76, 79, 83], [72, 76, 77, 81, 84], [69, 72, 74, 77, 81], [59, 71], [60, 72]]
paths = []
for i in itertools.product(*poss[0:3]):
    paths.append(list(i))
print(paths)
for path in paths:
    ctp_draft[0:3] = path
    print(ctp_draft)
def _recursive_search(self, ctp_draft, error, search_window, poss):
    paths = []
    for i in itertools.product(*poss[search_window[0]:search_window[1] + 1]):
        paths.append(list(i))
    ctp_draft[search_window[0]:search_window[1] + 1] = paths[0]
    best_ctp = ctp_draft
    error = error
    for path in paths:
        ctp_draft[search_window[0]:search_window[1] + 1] = path
        self.ctp_errors = []
        local_error = self.total_penalty(ctp_draft, self.cf_notes)
        if local_error < error:
            best_ctp = ctp_draft
            error = local_error
            if local_error < 100:
                return best_ctp, error
    return best_ctp, error

protected_indices = [0,1]
search_window = [0,1]
for elem in protected_indices:
    if elem in range(search_window[0],search_window[1]+1):
        print("hello!")