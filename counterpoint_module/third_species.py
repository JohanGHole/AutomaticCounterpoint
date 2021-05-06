from counterpoint_module.second_species import *

class ThirdSpecies(SecondSpecies):
    def __init__(self,cf,ctp_position = "above"):
        super(ThirdSpecies,self).__init__(cf,ctp_position)
        super(ThirdSpecies,self).generate_ctp(post_ornaments=False)
        self.ERROR_THRESHOLD = 200

    def get_harmonic_possibilities3(self, idx, cf_notes,ctp_notes):
        poss = super(ThirdSpecies,self).get_harmonic_possibilities(cf_notes[idx])
        upbeats = self.get_upbeats()
        if idx in upbeats:
            if idx != 1:
                poss = super(SecondSpecies, self).get_harmonic_possibilities(cf_notes[idx])
                if abs(ctp_notes[idx+1]-ctp_notes[idx-1]) in [m3,M3]:
                    s = sign(ctp_notes[idx+1]-ctp_notes[idx-1])
                    s = int(s)
                    if ctp_notes[idx-1] + s*m2 in self.scale_pitches:
                        poss.append(ctp_notes[idx-1]+s*m2)
                    if ctp_notes[idx-1] + s*M2 in self.scale_pitches:
                        poss.append(ctp_notes[idx-1]+s*M2)
        return poss
    def _possible_notes3(self):
        poss = [None for elem in self.cf_notes]
        first_beats = [i for i in range(len(poss)) if i % 4 == 0]
        print("first beats:", first_beats)
        for i in range(len(self.cf_notes)):
            if i in first_beats or i == 1:
                poss[i] = [self.ctp_notes[i]]
            elif i == len(self.cf_notes) - 5:
                poss[i] = [self.ctp_notes[i]]
            elif i == len(self.cf_notes) - 1 or i == len(self.cf_notes)-2:
                poss[i] = [self.ctp_notes[i]]
            else:
                poss[i] = self.get_harmonic_possibilities3(i, self.cf_notes,self.ctp_notes)
        return poss
    def _initialize_ctp3(self):
        # Expanding the already generated first species results:
        self.melody_rhythm = [2]*len(self.cf.melody_rhythm)*4
        self.ctp_notes = [ele for ele in self.ctp_notes for i in range(2)]
        self.cf_notes = [ele for ele in self.cf_notes for i in range(2)]
        print("downbeats: ",self.get_downbeats())
        print("upbeats: ",self.get_upbeats())
        print("expanded cf_notes: ",self.cf_notes)
        print("expanded ctp notes: ",self.ctp_notes)
        poss = self._possible_notes3()
        print("poss: ",poss)
        ctp_notes = []
        for p in poss:
            ctp_notes.append(rm.choice(p))
        self.ctp_notes = ctp_notes
        return ctp_notes, poss

    def _path_search3(self,ctp_draft,cf_notes,error,search_window,poss,protected_indices):
        paths = []
        search_window = search_window
        if protected_indices != []:
            for idx in protected_indices:
                if idx in range(search_window[0],search_window[1]+1):
                    return ctp_draft, error
        for i in itertools.product(*poss[search_window[0]:search_window[1]+1]):
            paths.append(list(i))
        ctp_draft[search_window[0]:search_window[1]+1] = paths[0]
        best_ctp = ctp_draft.copy()
        error = error
        best_local_error = math.inf
        for path in paths:
            ctp_draft[search_window[0]:search_window[1] + 1] = path
            self.ctp_errors = []
            local_error = self.total_penalty(ctp_draft,cf_notes)
            if  local_error < best_local_error:
                best_ctp = ctp_draft.copy()
                best_local_error = local_error
        return best_ctp.copy(), best_local_error

    def _search3(self,ctp_draft,cf_notes,poss):
        error = math.inf
        best_scan_error = math.inf
        j = 1
        protected_indices = []
        best_ctp = ctp_draft.copy()
        while error >= self.ERROR_THRESHOLD and j <= 6:
            error_window = math.inf
            for i in range(len(ctp_draft)):
                window_n = self._get_indices(i,j)
                ctp_draft, error = self._path_search2(best_ctp.copy(),cf_notes,error,window_n,poss,protected_indices)
                check = self.ctp_errors
                if i == 0:
                    error_window = error
                if error < best_scan_error:
                    best_ctp = ctp_draft.copy()
                    best_scan_error = error
                    if error < self.ERROR_THRESHOLD:
                        return best_scan_error, best_ctp
            if error_window <= best_scan_error:
                # No improvement, expand the window
                j += 1
        return best_scan_error,best_ctp

    def generate_ctp(self, post_ornaments = True):
        print("cf notes in generate_ctp: ",self.cf_notes)
        print("ctp notes in generate_ctp:",self.ctp_notes)
        print("first species error: ",self.error)
        ctp_shell, poss = self._initialize_ctp3()
        cf_notes = self.cf_notes
        error, ctp_shell = self._search3(ctp_shell,cf_notes,poss)
        self.ctp_notes = ctp_shell.copy()
        self.ctp_errors = []
        self.error_idx = []
        self.error = self.total_penalty(ctp_shell,cf_notes)
        print("ctp errors: ",self.ctp_errors)
        print("ctp error score: ",self.error)
        print("ctp_notes: ",self.ctp_notes)
        print("error idx: ",self.error_idx)
        if post_ornaments:
            self.ctp_notes[0] = -1
            self.ctp_notes[-4] = self.ctp_notes[-1]
            self.ctp_notes.pop(-1)
            self.ctp_notes.pop(-1)
            self.ctp_notes.pop(-1)
            self.melody_rhythm.pop(-1)
            self.melody_rhythm.pop(-1)
            self.melody_rhythm.pop(-1)
            self.melody_rhythm[-1] = 8

"""cf = Cantus_Firmus("C","major",bar_length = 1)
cf.generate_cf()
ctp = ThirdSpecies(cf,ctp_position="above")
print(ctp.initialize_ctp2())"""
