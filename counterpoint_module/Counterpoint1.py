from music_module.constants import *
import music_module.melody as m
from counterpoint_module.cf import *

class Counterpoint:
    melodic_intervals = [Unison,m2,M2,m3,M3,P4,P5,P8,-m2,-M2,-m3,-M3,-P4,-P5,-P8]
    dissonant_intervals = [m2,M2,M7,m7,P8+m2,P8+M2]
    harmonic_consonances = [m3,M3,P5,m6,M6,P8,P8+m3,P8+M3]
    perfect_intervals = [P5,P8]
    def __init__(self,cf,above_cf = True, species = "first"):
        self.key = cf.key
        self.cf = cf
        self.melody_rhythm = cf.melody_rhythm.copy()
        self.scale_name = cf.scale_name
        self.species = species
        self.above_cf = above_cf
        self.cf_notes = cf.melody
        self.cf_rhythm = cf.melody_rhythm
        if above_cf:
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
        self.ctp_melody = None
        self.ctp_errors = []
        self.ERROR_THRESHOLD = 50
        self.error_idx = []
    """ HELP FUNCTIONS """

    def motion(self,idx,upper_voice,lower_voice):
        if idx == 0:
            return
        cf = upper_voice
        ctp = lower_voice
        cf_dir = cf[idx]-cf[idx-1]
        ctp_dir = ctp[idx]-ctp[idx-1]
        if cf_dir == ctp_dir:
            return "parallel"
        elif (cf_dir == 0 and ctp_dir != 0) or (ctp_dir == 0 and cf_dir != 0):
            return "oblique"
        elif sign(cf_dir) == sign(ctp_dir) and cf_dir != ctp_dir:
            return "similar"
        else:
            return "contrary"

    def _get_interval_degree(self,interval):
        if interval == 0:
            return "unison"
        elif interval in [m2,M2]:
            return "second"
        elif interval in [m3,M3]:
            return "third"
        elif interval == P4:
            return "fourth"
        elif interval == P5:
            return "fifth"
        elif interval in [m6,M6]:
            return "sixth"
        elif interval in [m7,M7]:
            return "seventh"
        elif interval == Octave:
            return "octave"
        elif interval in [Octave+m2,Octave+M2]:
            return "ninth"
        elif interval in [Octave+m3,Octave+M3]:
            return "tenth"

    def _is_large_leap(self,ctp_draft,idx):
        if idx == len(ctp_draft)-1:
            return False
        if abs(ctp_draft[idx+1]-ctp_draft[idx]) >= P4:
            return True
        return False

    def _is_small_leap(self,ctp_draft,idx):
        if idx == len(ctp_draft)-1:
            return False
        if abs(ctp_draft[idx+1]-ctp_draft[idx]) in [m3,M3]:
            return True
        return False

    def _is_step(self,ctp_draft,idx):
        if idx == len(ctp_draft)-1:
            return False
        if abs(ctp_draft[idx+1]-ctp_draft[idx]) in [m2,M2]:
            return True
        return False

    """ MELODIC RULES """
    def _is_melodic_leap_too_large(self,ctp_draft,idx):
        if idx == len(ctp_draft)-1:
            return False
        interval = ctp_draft[idx+1] - ctp_draft[idx]
        if abs(interval) > P5:
            if sign(interval) == 1.0 and interval == m6 and self.species not in ["third","fifth"]:
                return False
            if abs(interval) == Octave:
                return False
            return True
        else:
            return False

    def _is_melodic_leap_octave(self,ctp_draft,idx):
        if idx == len(ctp_draft)-1:
            return False
        interval = ctp_draft[idx+1]-ctp_draft[idx]
        if abs(interval) == Octave:
            return True
        return False

    def _is_successive_same_direction_leaps(self,ctp_draft,idx):
        if idx >= len(ctp_draft)-2:
            return False
        interval1 = ctp_draft[idx+1]-ctp_draft[idx]
        interval2 = ctp_draft[idx+2]-ctp_draft[idx+1]
        if abs(interval1) >= m3 and abs(interval2) >= m3:
            if sign(interval1) != sign(interval2):
                return False
            if abs(interval1) + abs(interval2) <= M3+M3:
                # Outlines a triad, acceptable
                return False
            return True

    def _is_successive_leaps_valid(self,ctp_draft,idx):
        if idx >= len(ctp_draft)-2:
            return True
        interval1 = ctp_draft[idx + 1] - ctp_draft[idx]
        interval2 = ctp_draft[idx + 2] - ctp_draft[idx + 1]
        if abs(interval1) >= m3 and abs(interval2) >= m3:
            if abs(interval1) + abs(interval2) >= Octave:
                return False
            if sign(interval1) == sign(interval2) == 1.0:
                if interval2 > interval1:
                    return False
            if sign(interval1) == sign(interval2) == -1.0:
                if abs(interval1) > abs(interval2):
                    return False
        return True

    def _is_leap_compensated(self,ctp_draft,idx):
        if idx >= len(ctp_draft)-2:
            return True
        interval1 = ctp_draft[idx+1]-ctp_draft[idx]
        interval2 = ctp_draft[idx+2]-ctp_draft[idx+1]
        if abs(interval1) >= P5:
            if sign(interval1) == 1.0 and sign(interval2) == -1.0 and abs(interval2) <= M2:
                return True
            elif sign(interval1) == -1.0 and sign(interval2) == 1.0 and abs(interval2) <= M3:
                return True
            else:
                return False
        return True

    def _is_octave_compensated(self,ctp_draft,idx):
        if idx >= len(ctp_draft)-3:
            return True
        interval1 = ctp_draft[idx+1]-ctp_draft[idx]
        interval2 = ctp_draft[idx+2]-ctp_draft[idx+1]
        if self._is_melodic_leap_octave(ctp_draft,idx+1):
            if self._is_leap_compensated(ctp_draft,idx+1) and sign(interval1) != sign(interval2):
                return True
            else:
                return False
        else:
            return True

    def _is_chromatic_step(self,ctp_draft,idx):
        if idx >= len(ctp_draft)-1:
            return False
        if abs(ctp_draft[idx+1]-ctp_draft[idx]) == 1 and ctp_draft[idx+1] not in self.scale_pitches:
            return True
        return False

    def _is_within_range_of_a_tenth(self,ctp_draft):
        if max(ctp_draft) - min(ctp_draft) >= Octave+M3:
            return False
        else:
            return True

    def _is_repeating_pitches(self,ctp_draft):
        total = 0
        if self.above_cf:
            for i in range(len(ctp_draft)-1): # was 2
                if ctp_draft[i] == ctp_draft[i+1]: #== ctp_draft[i+2]:
                    total += 1
        else:
            for i in range(len(ctp_draft) - 1):
                if ctp_draft[i] == ctp_draft[i + 1]:
                    total += 1
        return total

    def _is_unique_climax(self,ctp_draft):
        # Unique climax that is different from the cantus firmus
        if ctp_draft.count(max(ctp_draft)) == 1 and (ctp_draft.index(max(ctp_draft)) != self.cf_notes.index(max(self.cf_notes))):
            return True
        else:
            return False

    def melodic_rules(self,ctp_draft):
        penalty = 0
        # Index based rules
        for i in range(len(ctp_draft)):
            if self._is_melodic_leap_too_large(ctp_draft,i):
                self.ctp_errors.append("Too large leap!")
                penalty += 100
            if self._is_melodic_leap_octave(ctp_draft,i):
                self.ctp_errors.append("Octave leap!")
                penalty += 25
            if not self._is_leap_compensated(ctp_draft,i):
                self.ctp_errors.append("Leap not compensated!")
                penalty += 25
            if not self._is_octave_compensated(ctp_draft,i):
                self.ctp_errors.append("Octave not compensated!")
                penalty += 25
            if self._is_successive_same_direction_leaps(ctp_draft,i):
                self.ctp_errors.append("Successive Leaps in same direction!")
                penalty += 10
                if not self._is_successive_leaps_valid(ctp_draft,i):
                    self.ctp_errors.append("Successive leaps strictly not valid!")
                    penalty += 100
            if self._is_chromatic_step(ctp_draft,i):
                self.ctp_errors.append("Chromatic movement!")
                penalty += 100
        # Global rules
        if not self._is_within_range_of_a_tenth(ctp_draft):
            self.ctp_errors.append("Exceeds the range of a tenth!")
            penalty += 100
        if self._is_repeating_pitches(ctp_draft) > 0:
            self.ctp_errors.append("Repeats pitches!")
            penalty += 25*self._is_repeating_pitches(ctp_draft)
        if not self._is_unique_climax(ctp_draft):
            self.ctp_errors.append("No unique climax or at same position as other voices!")
            penalty += 100
        return penalty

    """ RHYTHMIC RULES """
    def get_rhythm(self):
        "Voices all move together in the same rhythm as the cantus firmus."
        return [8]*len(self.cf_notes)

    """ VOICE INDEPENDENCE RULES """
    def _is_perfect_interval_properly_approached(self,upper_voice,lower_voice,idx):
        if idx == 0: # the start interval MUST be a perfect interval and is therefore allowed
            return True
        if upper_voice[idx]-lower_voice[idx] in self.perfect_intervals:
            if self.motion(idx,upper_voice,lower_voice) not in ["oblique","contrary"]:
                return False
            if self._is_large_leap(upper_voice,idx-1) or self._is_large_leap(lower_voice,idx-1):
                if upper_voice[idx]-lower_voice[idx] == Octave:
                    if self.motion(idx,upper_voice,lower_voice) == "oblique" or idx == len(upper_voice)-1:
                        return True
                else:
                    return False
        return True

    def _is_valid_consecutive_perfect_intervals(self,upper_voice,lower_voice,idx):
        if idx >= len(upper_voice) - 1:
            return True
        harm_int1 = upper_voice[idx]-lower_voice[idx]
        harm_int2 = upper_voice[idx+1]-lower_voice[idx+1]
        if harm_int1 in self.perfect_intervals and  harm_int2 in self.perfect_intervals:
            if self._is_step(upper_voice,idx) or self._is_step(lower_voice,idx):
                return True
            else:
                return False
        return True

    def _is_parallel_fourths(self,upper_voice,lower_voice,idx):
        if idx == len(upper_voice)-1:
            return False
        if self.motion(idx,upper_voice,lower_voice) == "parallel" and upper_voice[idx]-lower_voice[idx] == P4:
            return True
        return False

    def _is_voice_overlapping(self,upper_voice,lower_voice,idx):
        if idx < len(lower_voice) - 1 and lower_voice[idx + 1] >= upper_voice[idx]:
            return True
        return False

    def _is_voice_crossing(self,upper_voice,lower_voice,idx):
        if upper_voice[idx] - lower_voice[idx] < 0:
            return True
        return False

    def _is_contrary_motion(self,upper_voice,lower_voice,idx):
        if self.motion(idx,upper_voice,lower_voice) == "contrary":
            return True
        else:
            return False

    def _is_valid_number_of_consecutive_intervals(self,upper_voice,lower_voice):
        valid = True
        for i in range(len(lower_voice)-3):
            i1 = self._get_interval_degree(upper_voice[i]-lower_voice[i])
            i2 = self._get_interval_degree(upper_voice[i+1] - lower_voice[i+1])
            i3 = self._get_interval_degree(upper_voice[i+2] - lower_voice[i+2])
            i4 = self._get_interval_degree(upper_voice[i+3] - lower_voice[i+3])
            if i1 == i2 == i3 == i4:
                valid = False
        return valid

    def _is_unisons_between_terminals(self,ctp):
        return ctp[1:-1].count(self.cf_tonic)

    def voice_independence_rules(self,ctp_draft,cf_notes):
        if self.above_cf:
            upper_voice = ctp_draft
            lower_voice = cf_notes
        else:
            upper_voice = cf_notes
            lower_voice = ctp_draft
        penalty = 0
        # Index based rules
        for i in range(len(ctp_draft)):
            if not self._is_perfect_interval_properly_approached(upper_voice,lower_voice,i):
                self.ctp_errors.append("Perfect interval not properly approached!")
                penalty += 100
            if not self._is_valid_consecutive_perfect_intervals(upper_voice,lower_voice,i):
                self.ctp_errors.append("Consecutive perfect intervals, but they are not valid!")
                penalty += 100
            if self._is_parallel_fourths(upper_voice,lower_voice,i):
                self.ctp_errors.append("Parallel fourths!")
                penalty += 50
            if self._is_voice_overlapping(upper_voice,lower_voice, i):
                self.ctp_errors.append("Voice Overlapping!")
                penalty += 100
            if self._is_voice_crossing(upper_voice,lower_voice,i):
                self.ctp_errors.append("Voice crossing!")
                penalty += 50
            if self._is_contrary_motion(upper_voice,lower_voice, i):
                    # This not not a severe violation, but more of a preference to avoid similar motion
                    penalty += 5
        # Global rules
        if not self._is_valid_number_of_consecutive_intervals(upper_voice,lower_voice):
            self.ctp_errors.append("Too many consecutive intervals!")
            penalty += 100
        if self._is_unisons_between_terminals(ctp_draft) > 0:
            self.ctp_errors.append("Unison between terminals!")
            penalty += 25*self._is_unisons_between_terminals(ctp_draft)
        return penalty

    """ DISSONANT RULES"""
    def dissonant_rules(self,ctp_draft):
        # In first species there is no dissonance, so the allowed harmonic intervals are consonances
        return 0

    """ HARMONIC RULES """
    def _is_valid_terminals(self,ctp_draft,cf_notes):
        # check start and end pitches and see if they are valid
        # must begin and end with perfect consonances (octaves, fifths or unison)
        # Octaves or unisons preferred at the end (i.e. perfect fifth not allowed)
        # if below, the start and end must be the octave the cf
        if self.above_cf:
            if (ctp_draft[0]-cf_notes[0] not in [Unison,P5,Octave]) or (ctp_draft[-1]-cf_notes[-1] not in [Unison,Octave]):
                return False
            else:
                return True
        else:
            if (cf_notes[0]-ctp_draft[0] not in [Unison,Octave]) or (cf_notes[-1]-ctp_draft[-1] not in [Unison,Octave]):
                return False
            else:
                return True

    def _no_outlined_tritone(self,ctp_draft):
        outline_idx = [0]
        outline_intervals = []
        not_allowed_intervals = [Tritone, m7, M7]
        # mellom ytterkant og inn + endring innad
        dir = [sign(ctp_draft[i + 1] - ctp_draft[i]) for i in range(len(ctp_draft) - 1)]
        for i in range(len(dir) - 1):
            if dir[i] != dir[i + 1]:
                outline_idx.append(i + 1)
        outline_idx.append(len(ctp_draft) - 1)
        # Iterate over the outline indices and check if a tritone is found
        for i in range(len(outline_idx) - 1):
            outline_intervals.append(abs(ctp_draft[outline_idx[i]] - ctp_draft[outline_idx[i + 1]]))

        for interval in not_allowed_intervals:
            if interval in outline_intervals:
                return False

        return True

    def harmonic_rules(self,ctp_draft,cf_notes):
        penalty = 0
        if not self._is_valid_terminals(ctp_draft,cf_notes):
            self.ctp_errors.append("Terminals not valid!")
            penalty += 100
        if not self._no_outlined_tritone(ctp_draft):
            self.ctp_errors.append("Outlined dissonant interval!")
            penalty += 100
        return penalty

    """ TOTAL PENALTY"""
    def total_penalty(self,ctp_draft,cf_notes):
        penalty = 0
        penalty += self.melodic_rules(ctp_draft)
        penalty += self.voice_independence_rules(ctp_draft,cf_notes)
        penalty += self.dissonant_rules(ctp_draft)
        penalty += self.harmonic_rules(ctp_draft,cf_notes)
        return penalty

    """ HELP FUNCTIONS FOR INITIALIZING COUNTERPOINT"""

    def _start_notes(self):
        if self.above_cf:
            return [self.cf_tonic,self.cf_tonic + P5, self.cf_tonic + Octave]
        else:
            return [self.cf_tonic - Octave,self.cf_tonic]

    def _end_notes(self):
        if self.above_cf:
            return [self.cf_tonic, self.cf_tonic + Octave]
        else:
            return [self.cf_tonic, self.cf_tonic - Octave]

    def _penultimate_notes(self, cf_end):  # Bug in penultimate
        if self.above_cf:
            s = 1
        else:
            s = -1
        if self.cf_direction[-1] == 1.0:
            penultimate = cf_end + 2
        else:
            penultimate = cf_end - 1
        return [penultimate, penultimate + s * Octave]

    def get_harmonic_possibilities(self,cf_note):
        poss = []
        for interval in self.harmonic_consonances:
            if self.above_cf:
                if cf_note+interval in self.scale_pitches:
                    poss.append(cf_note+interval)
            else:
                if cf_note-interval in self.scale_pitches:
                    poss.append(cf_note-interval)
        return poss

    def _possible_notes(self):
        poss = [None for elem in self.cf_notes]
        for i in range(len(self.cf_notes)):
            if i == 0:
                poss[i] = self._start_notes()
            elif i == len(self.cf_notes)-2:
                poss[i] = self._penultimate_notes(self.cf_notes[i+1])
            elif i == len(self.cf_notes)-1:
                poss[i] = self._end_notes()
            else:
                poss[i] = self.get_harmonic_possibilities(self.cf_notes[i])
        return poss

    """ INITIALIZING COUNTERPOINT WITH RANDOM VALUES"""

    def _initialize_ctp(self):
        self.melody_rhythm = self.get_rhythm()
        poss = self._possible_notes()
        ctp_notes = []
        for p in poss:
            ctp_notes.append(rm.choice(p))
        return ctp_notes, poss