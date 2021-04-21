import music_module.music as m
from music_module.constants import *
from counterpoint_module.cf import *
import math
import pretty_midi
"""
TODO: The hard rules of counterpoint (taken from the study of counterpoint):
    1) For every note of the cantus firmus there is one note in the counterpoint (check)
    2) diatonic except raised leading tone in minor  (check)
    3) All harmonies must be consonant (a perfect fourth is considered a dissonance) (check)
    4) The first interval must be any perfect harmony and the last an octave or unison (check)
    5) The last interval must be approached by motion of a minor second upwards (note rule 8 may not be broken) (check)
    6) All perfect intervals must be approached by contrary motion
    7) motion can proceed by step or leap but steps and leaps of augmented and diminished intervals and leaps of any seventh
       are forbidden. Leaps greater than a ascending sixth are forbidden except for leaps of an octave which should be rare
    8) The counterpoint may not outline an interval of a tritone or seventh except for an augmented fourth that is fully,
       stepwise outlined and precedes an inwards step
None of the abovementioned rules may be broken
TODO: Soft rules of counterpoint
    1) No note may be repeated successively more than three times V - Changed to 2 times! V
    2) No two successive leaps in the same direction may total more than an octave V
    3) while ascending, in the case of two successive steps or leaps, the larger one should precede the smaller; while descending the smaller
       should precede the larger V
    4) No successive leaps in opposite directions; leaps should be followed by inward, stepwise motion V
    5) The same harmonic interval should not repeat more than three times
    6) There should be no more than two successive leaps
    7) The range of the counterpoint should be limited to a tenth and all notes in the chosen mode should appear in the counterpoint

"""


class FirstSpecies:
    melodic_intervals = [Unison,m2,M2,m3,M3,P4,P5,P8,-m2,-M2,-m3,-M3,-P4,-P5,-P8]
    harmonic_consonances = [m3,M3,P5,m6,M6,P8,P8+m3,P8+M3]
    perfect_intervals = [P5,P8]
    def __init__(self,cf,ctp_position = "above"):
        self.key = cf.key
        self.cf = cf
        self.melody_rhythm = cf.melody_rhythm
        self.scale_name = cf.scale_name
        self.ctp_position = ctp_position
        self.cf_notes = cf.melody
        self.cf_rhythm = cf.melody_rhythm
        if ctp_position == "above":
            try:
                self.voice_range = RANGES[RANGES.index(cf.voice_range)+1]
            except:
                print("ERROR. the Cantus Firmus is in the top voice. Writing ctp below instead..")
                self.voice_range = RANGES[RANGES.index(cf.voice_range)-1]
        else:
            try:
                self.voice_range = RANGES[RANGES.index(cf.voice_range)-1]
            except:
                print("ERROR. the Cantus Firmus is in the lowest voice. Writing ctp above instead..")
                self.voice_range = RANGES[RANGES.index(cf.voice_range)+1]
        self.scale = m.Scale(self.key,self.scale_name, self.voice_range)
        self.scale_pitches = self.scale.get_scale_pitches()
        self.ctp_notes = [None for elem in self.cf_notes]
        self.ctp_tonic = cf.start_note+(RANGES.index(self.voice_range)-RANGES.index(cf.voice_range))*Octave
        self.cf_tonic = cf.start_note
        self.cf_direction = [sign(self.cf_notes[i]-self.cf_notes[i-1]) for i in range(1,len(self.cf_notes))]
        self.ctp_notes,self.poss = self._initialize_cpt()
        self.ctp_melody = None
        self.ctp_errors = []

    """ HELP FUNCTIONS FOR INITIALIZING COUNTERPOINT"""
    def _start_notes(self):
        if self.ctp_position == "above":
            return [self.cf_tonic+P5,self.cf_tonic+Octave]#[self.cf_tonic,self.cf_tonic+P5,self.cf_tonic+Octave]
        else:
            return [self.cf_tonic-Octave]

    def _end_notes(self):
        if self.ctp_position == "above":
            return [self.cf_tonic+Octave]#[self.cf_tonic,self.cf_tonic+Octave]
        else:
            return [self.cf_tonic-Octave]#[self.cf_tonic,self.cf_tonic-Octave]

    def _penultimate_notes(self,cf_end): # Bug in penultimate
        if self.ctp_position == "above":
            s = 1
        else:
            s = -1
        if self.cf_direction[-1] == 1.0:
            penultimate = cf_end + 2
        else:
            penultimate = cf_end - 1
        #if self.scale_name == "minor" and self.cf_direction[-1] == -1.0:
            #penultimate += 1
        return [penultimate,penultimate+s*Octave]

    def _get_harmonic_possibilities(self,cf_note):
        poss = []
        for interval in self.harmonic_consonances:
            if self.ctp_position == "above":
                if cf_note+interval in self.scale_pitches:
                    poss.append(cf_note+interval)
            else:
                if cf_note-interval in self.scale_pitches:
                    poss.append(cf_note-interval)
        return poss

    def _get_list_of_possible_notes(self):
        poss = [None for elem in self.cf_notes]
        for i in range(len(self.cf_notes)):
            if i == 0:
                poss[i] = self._start_notes()
            elif i == len(self.cf_notes)-2:
                poss[i] = self._penultimate_notes(self.cf_notes[i+1])
            elif i == len(self.cf_notes)-1:
                poss[i] = self._end_notes()
            else:
                poss[i] = self._get_harmonic_possibilities(self.cf_notes[i])
        return poss

    def _motion(self,idx,ctp_shell):
        if idx == 0:
            return
        cf = self.cf_notes
        ctp = ctp_shell
        cf_dir = cf[idx]-cf[idx-1]
        ctp_dir = ctp[idx]-cf[idx-1]
        if cf_dir == ctp_dir:
            return "parallel"
        elif (cf_dir == 0 and ctp_dir != 0) or (ctp_dir == 0 and cf_dir != 0):
            return "oblique"
        elif sign(cf_dir) == sign(ctp_dir) and cf_dir != ctp_dir:
            return "similar"
        else:
            return "contrary"

    def _initialize_cpt(self):
        poss = self._get_list_of_possible_notes()
        ctp_notes = []
        for p in poss:
            ctp_notes.append(rm.choice(p))
        return ctp_notes,poss

    """ GLOBAL RULE PENALTIES"""
    def _check_climax(self,ctp_shell):
        # Unique climax that is different from the cantus firmus
        if ctp_shell.count(max(ctp_shell)) == 1 and (ctp_shell.index(max(ctp_shell)) != self.cf_notes.index(max(self.cf_notes))):
            return 0
        else:
            self.ctp_errors.append("No unique climax that is different from the cf")
            return 150

    def _valid_range(self,ctp_shell):
        if abs(max(ctp_shell)-min(ctp_shell)) > Octave+M3:
            self.ctp_errors.append("Range too wide")
            return 150
        else:
            return 0

    def _check_outlines(self,ctp_shell):
        outline_idx = [0]
        outline_intervals = []
        not_allowed_intervals = [Tritone, m7, M7]
        # mellom ytterkant og inn + endring innad
        dir = [sign(ctp_shell[i + 1] - ctp_shell[i]) for i in range(len(ctp_shell) - 1)]
        for i in range(len(dir) - 1):
            if dir[i] != dir[i + 1]:
                outline_idx.append(i + 1)
        outline_idx.append(len(ctp_shell) - 1)
        # Iterate over the outline indices and check if a tritone is found
        for i in range(len(outline_idx) - 1):
            outline_intervals.append(abs(ctp_shell[outline_idx[i]] - ctp_shell[outline_idx[i + 1]]))

        for interval in not_allowed_intervals:
            if interval in outline_intervals:
                self.ctp_errors.append("Outlining a seventh or tritone")
                return 150

        return 0

    """Index based global """
    def _check_melodic_intervals(self,idx,ctp_shell):
        if idx == 0:
            return 0
        if ctp_shell[idx]-ctp_shell[idx-1] not in self.melodic_intervals:
            self.ctp_errors.append("dissonant melodic interval")
            return 150
        elif abs(ctp_shell[idx]-ctp_shell[idx-1]) is Octave:
            self.ctp_errors.append("Octave leap, small penalty")
            return 50
        else:
            return 0

    def _check_perfect_intervals(self,idx,ctp_shell):
        if idx == 0:
            return 0
        if self.ctp_position == "above":
            lowest_voice = self.cf_notes
            upper_voice = ctp_shell
        else:
            lowest_voice = ctp_shell
            upper_voice = self.cf_notes
        if upper_voice[idx]-lowest_voice[idx] in self.perfect_intervals and self._motion(idx,ctp_shell) not in ["contrary","oblique"]:
            self.ctp_errors.append("Perfect interval approached by wrong motion")
            return 150
        return 0

    def _check_voice_crossing(self,idx, ctp_shell):
        if self.ctp_position == "above":
            upper_voice = ctp_shell
            lower_voice = self.cf_notes
        else:
            upper_voice = self.cf_notes
            lower_voice = ctp_shell
        if idx < len(ctp_shell)-1 and lower_voice[idx+1] > upper_voice[idx]:
            self.ctp_errors.append("voice overlapping")
            return 150
        if upper_voice[idx]-lower_voice[idx] < 0:
            self.ctp_errors.append("Voice crossing")
            return 150
        else:
            return 0

    def _check_leaps(self,idx,ctp_shell):
        if idx == 0:
            return 0
        elif idx == len(ctp_shell)-1:
            return 0
        ctp = ctp_shell
        next_leap = ctp[idx+1]-ctp[idx]
        next_dir = sign(next_leap)
        prev_leap = ctp[idx]-ctp[idx-1]
        prev_dir = sign(prev_leap)
        score = 0
        if abs(prev_leap) >= P4: # large leap
            if abs(next_leap) in [m2,M2] and prev_dir == next_dir:
                score += 50
                self.ctp_errors.append("A leap is not properly recovered")
            elif abs(next_leap) >= P4 and prev_dir != next_dir:
                self.ctp_errors.append("Large successive leaps in opposite direction")
                score += 100
            elif abs(next_leap) >= P4 and prev_dir == next_dir == 1.0 and prev_leap <= next_leap:
                self.ctp_errors.append("successive ascending leaps with the smaller preceding the larger")
                score += 50
            elif (abs(next_leap) >= P4) and (prev_dir == next_dir == -1.0) and (abs(prev_leap) >= abs(next_leap)):
                self.ctp_errors.append("successive descending leaps with the larger preceding the smaller")
                score += 50
        return score

    def _check_repeated_notes(self,idx,ctp_shell):
        # check successive repeated notes and if they are tonic if before == current == after: penalty. If tonic, penalty.
        if idx == 0 or idx == len(ctp_shell)-1:
            return 0
        ctp = ctp_shell
        score = 0
        if ctp[idx-1] == ctp[idx] == ctp[idx+1]:
            self.ctp_errors.append("repeated notes")
            score += 50
        if ctp[idx] == self.cf_tonic:
            self.ctp_errors.append("tonic inside end points")
            score += 50
        return score

    def _check_harmonic_motion(self,idx,ctp_shell):
        if idx == len(ctp_shell)-1:
            return 0
        if self.ctp_position == "above":
            upper_voice = ctp_shell
            lower_voice = self.cf_notes
        else:
            upper_voice = self.cf_notes
            lower_voice = ctp_shell
        if abs(upper_voice[idx] - lower_voice[idx]) in self.perfect_intervals and abs(upper_voice[idx+1]-lower_voice[idx+1]) in self.perfect_intervals:
            self.ctp_errors.append("Successive perfect intervals")
            return 100
        return 0

    def _strict_rules_penalty(self,ctp_shell):
        """ NONE OF THE FOLLOWING RULES MIGHT BE BROKEN => PENALTY FOR EACH >= 150"""
        penalty = 0
        for i in range(len(ctp_shell)):
            penalty += self._check_melodic_intervals(i,ctp_shell)
            penalty += self._check_perfect_intervals(i,ctp_shell)
            penalty += self._check_voice_crossing(i,ctp_shell)
        penalty += self._check_outlines(ctp_shell)
        penalty += self._check_climax(ctp_shell)
        return penalty

    def _soft_rules_penalty(self,ctp_shell):
        """ SOME OF THE FOLLOWING RULES MIGHT BE BROKEN => PENALTY FOR EACH BETWEEN 25 AND 150"""
        # No more than two successively repeated notes. check
        # ascending and successive leaps: the larger before the smaller. check
        # descending and successive leaps: the smaller before the larger. check
        # Leaps should be followed by inward, stepwise motion check
        # The same harmonic interval should not repeat more than three times
        # maximum two successive leaps, and they need to be in the same direction
        penalty = 0
        for i in range(len(ctp_shell)):
            penalty += self._check_repeated_notes(i,ctp_shell)
            penalty += self._check_leaps(i,ctp_shell) # melodic + check inward stepwise motion + successive leaps max 2 + need to be in same direction
            penalty += self._check_harmonic_motion(i,ctp_shell) # no consecutive perfect intervals
        return penalty


    def _local_penalty(self,idx,ctp_draft):
        # Thirds and sixths better harmonic motion than others (local)
        # Pref contrary motion if possible (local)
        ctp_note = ctp_draft[idx]
        cf_note = self.cf_notes[idx]
        if self.ctp_position == "above":
            upper_note = ctp_note
            lower_note = cf_note
        else:
            upper_note = cf_note
            lower_note = ctp_note
        """Check harmonic"""
        penalty = 0
        if upper_note - lower_note not in [m3,M3,m6,M6]:
            penalty += 15 # very small
            self.ctp_errors.append("interval not third or sixth")
        if self._motion(idx,ctp_draft) != "contrary":
            penalty += 15
            self.ctp_errors.append("interval not contrary")
        return penalty
    def _global_penalty(self, ctp_shell):
        """
    6) All perfect intervals must be approached by contrary motion
    7) motion can proceed by step or leap but steps and leaps of augmented and diminished intervals and leaps of any seventh
       are forbidden. Leaps greater than a ascending sixth are forbidden except for leaps of an octave which should be rare
    8) The counterpoint may not outline an interval of a tritone or seventh except for an augmented fourth that is fully,
       stepwise outlined and precedes an inwards step
       No two successive leaps in the same direction may total more than an octave V
    3) while ascending, in the case of two successive steps or leaps, the larger one should precede the smaller; while descending the smaller
       should precede the larger V
    4) No successive leaps in opposite directions; leaps should be followed by inward, stepwise motion V
    5) The same harmonic interval should not repeat more than three times
    6) There should be no more than two successive leaps
    7) The range of the counterpoint should be limited to a tenth and all notes in the chosen mode should appear in the counterpoint"""
        # In range of a tenth of the other voice (Check)
        # no perfect intervals by direct or oblique motion (check)
        # skip in same direction BAD
        # prefer contrary motion
        # no outlines
        # has climax and climax_ctp != climax cf
        # pref thirds and sixths over perfect intervals
        # check successive notes. Max 2
        # The larger leap should precede the smaller in ascending successive steps or leaps. The opposite for descending (smaller first, then larger)
        # There should be no more than two successive leaps
        # range of a tenth
        penalty = self._strict_rules_penalty(ctp_shell)
        penalty += self._soft_rules_penalty(ctp_shell)
        return penalty

    def generate_ctp(self):
        t0 = time()
        total_penalty = math.inf
        iteration = 0
        while total_penalty >= 150 and iteration <= 1000:
            self.ctp_errors = []
            total_penalty = 0
            ctp_shell,poss = self._initialize_cpt() # initialized randomly
            for i in range(len(ctp_shell)):
                local_max = math.inf
                ctp_draft = ctp_shell.copy()
                mel_cons = poss[i]
                rm.shuffle(mel_cons) # randomize the order
                for notes in mel_cons:
                    ctp_draft[i] = notes
                    penalty = self._global_penalty(ctp_draft)
                    penalty += self._local_penalty(i, ctp_draft)
                    if penalty <= local_max:
                        local_max = penalty
                        best_choice = notes
                ctp_shell[i] = best_choice
                # test
            self.ctp_errors = []
            total_penalty += self._global_penalty(ctp_shell)
            iteration += 1
            #print("iter: ",iteration)
        self.ctp_notes = ctp_shell
        t1 = time()
        print("time for generating ctp: ",str((t1-t0)*1000)+"ms")
        print("errors in ctp: ",self.ctp_errors)
        print("Iterations: ",iteration)


    def construct_ctp_melody(self,start = 0):
        self.ctp_melody = m.Melody(self.key,self.scale,self.cf.bar_length,melody_notes=self.ctp_notes,melody_rhythm = self.melody_rhythm,start = start,voice_range = self.voice_range)
        return self.ctp_melody

