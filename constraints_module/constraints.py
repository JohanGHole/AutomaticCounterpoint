from music_module.constants import *
from itertools import chain
class Constraints:
    melodic_intervals = [Unison, m2, M2, m3, M3, P4, P5, P8, -m2, -M2, -m3, -M3, -P4, -P5, -P8]
    dissonant_intervals = [m2, M2, P4, M7, m7, P8 + m2, P8 + M2]
    harmonic_consonances = [m3, M3, P5, m6, M6, P8, P8 + m3, P8 + M3]
    perfect_intervals = [P5, P8]
    def __init__(self,ctp):
        self.species = ctp.species
        self.ctp = ctp.ctp.melody.copy()
        self.short_cf = ctp.cf.melody.copy()
        self.ctp_rhythm = ctp.ctp.melody_rhythm.copy()
        self.ctp_flat_rhythm = list(chain.from_iterable(self.ctp_rhythm))
        self.ctp_in_measure = self.convert_pitch_sequence_to_measures()
        self.measure_idx = []
        j = 0
        for i in range(len(self.ctp_rhythm)):
            self.measure_idx.append(j)
            for k in range(len(self.ctp_rhythm[i])):
                j += 1
        self.scale_pitches = ctp.scale_pitches
        self.cf_notes = self.extend_cf(ctp.cf.melody.copy())
        self.cf_tonic = self.cf_notes[0]
        self.ties = ctp.ctp.ties
        self.ctp_position = ctp.ctp_position
        self.ctp_errors = []
        self.start_idx = self._get_numb_start_idx()
        self.end_idx = [len(self.ctp)-1]
        self.weighted_indices = {}
        for i in range(len(self.ctp)):
            self.weighted_indices[i] = 0
        """ HELP FUNCTIONS """
    def extend_cf(self,cf):
        cf_extended = []
        for m in range(len(self.ctp_rhythm)):
            for n in range(len(self.ctp_rhythm[m])):
                cf_extended.append(cf[m])
        return cf_extended
    def convert_pitch_sequence_to_measures(self):
        pitch_measures = []
        i = 0
        for j in range(len(self.ctp_rhythm)):
            measure = []
            for note_dur in range(len(self.ctp_rhythm[j])):
                measure.append(self.ctp[i])
                i += 1
            pitch_measures.append(measure)
        return pitch_measures

    def _get_numb_start_idx(self):
        if SPECIES[self.species] == 1:
            return [0]
        elif SPECIES[self.species] in [2,3,4,5]:
            return [0,1]

    def motion(self, idx, upper_voice, lower_voice):
        if idx == 0 or upper_voice[0] == -1 or lower_voice[0] == -1:
            return
        cf = upper_voice
        ctp = lower_voice
        cf_dir = cf[idx] - cf[idx - 1]
        ctp_dir = ctp[idx] - ctp[idx - 1]
        if cf_dir == ctp_dir:
            return "parallel"
        elif (cf_dir == 0 and ctp_dir != 0) or (ctp_dir == 0 and cf_dir != 0):
            return "oblique"
        elif sign(cf_dir) == sign(ctp_dir) and cf_dir != ctp_dir:
            return "similar"
        else:
            return "contrary"

    def _get_interval_degree(self, interval):
        if interval == 0:
            return "unison"
        elif interval in [m2, M2]:
            return "second"
        elif interval in [m3, M3]:
            return "third"
        elif interval == P4:
            return "fourth"
        elif interval == P5:
            return "fifth"
        elif interval == d5:
            return "d5"
        elif interval in [m6, M6]:
            return "sixth"
        elif interval in [m7, M7]:
            return "seventh"
        elif interval == Octave:
            return "octave"
        elif interval in [Octave + m2, Octave + M2]:
            return "ninth"
        elif interval in [Octave + m3, Octave + M3]:
            return "tenth"

    def _is_large_leap(self, ctp_draft, idx):
        if idx == len(ctp_draft) - 1 or ctp_draft[idx] == -1:
            return False
        if abs(ctp_draft[idx + 1] - ctp_draft[idx]) >= P4:
            return True
        return False

    def _is_small_leap(self, ctp_draft, idx):
        if idx == len(ctp_draft) - 1 or ctp_draft[idx] == -1:
            return False
        if abs(ctp_draft[idx + 1] - ctp_draft[idx]) in [m3, M3]:
            return True
        return False

    def _is_step(self, ctp_draft, idx):
        if idx == len(ctp_draft) - 1 or ctp_draft[idx] == -1:
            return False
        if abs(ctp_draft[idx + 1] - ctp_draft[idx]) in [m2, M2]:
            return True
        return False

    def get_firstbeats(self):
        indices = list(range(len(self.cf_notes)))
        return indices[::4]
    def get_downbeats(self):
        indices = list(range(len(self.cf_notes)))
        return indices[::2]
    def get_upbeats(self):
        indices = list(range(len(self.cf_notes)))
        return indices[1::2]

    """ MELODIC RULES """

    def _is_melodic_leap_too_large(self, ctp_draft, idx):
        if idx in self.end_idx or ctp_draft[idx] == -1:
            return False
        interval = ctp_draft[idx + 1] - ctp_draft[idx]
        if abs(interval) > P5:
            if self.species == "fifth" and self.ctp_flat_rhythm[idx] < 4 and self.ctp_flat_rhythm[idx+1] < 4:
                return True
            if sign(interval) == 1.0 and interval == m6 and self.species not in ["third"]:
                return False
            if abs(interval) == Octave:
                return False
            return True
        else:
            return False

    def _is_melodic_leap_octave(self, ctp_draft, idx):
        if idx in self.end_idx or ctp_draft[idx] == -1:
            return False
        interval = ctp_draft[idx + 1] - ctp_draft[idx]
        if abs(interval) == Octave:
            return True
        return False

    def _is_successive_same_direction_leaps(self, ctp_draft, idx):
        if idx >= self.end_idx[0]-1 or ctp_draft[idx] == -1:
            return False
        interval1 = ctp_draft[idx + 1] - ctp_draft[idx]
        interval2 = ctp_draft[idx + 2] - ctp_draft[idx + 1]
        if abs(interval1) >= m3 and abs(interval2) >= m3:
            if sign(interval1) != sign(interval2):
                return False
            if abs(interval1) + abs(interval2) <= M3 + M3:
                # Outlines a triad, acceptable
                return False
            return True
        return False

    def _is_successive_leaps_valid(self, ctp_draft, idx):
        if idx >= self.end_idx[0]-1 or ctp_draft[idx] == -1:
            return True
        interval1 = ctp_draft[idx + 1] - ctp_draft[idx]
        interval2 = ctp_draft[idx + 2] - ctp_draft[idx + 1]
        if abs(interval1) >= m3 and abs(interval2) >= m3:
            if abs(interval1) + abs(interval2) > Octave:
                return False
            if sign(interval1) == sign(interval2) == 1.0:
                if interval2 > interval1:
                    return False
            if sign(interval1) == sign(interval2) == -1.0:
                if abs(interval1) > abs(interval2):
                    return False
        return True

    def _is_leap_compensated(self, ctp_draft, idx):
        if idx >= self.end_idx[0] - 1 or ctp_draft[idx] == -1:
            return True
        interval1 = ctp_draft[idx + 1] - ctp_draft[idx]
        interval2 = ctp_draft[idx + 2] - ctp_draft[idx + 1]
        if abs(interval1) > P5:
            if sign(interval1) == 1.0 and sign(interval2) == -1.0 and abs(interval2) <= M2:
                return True
            elif sign(interval1) == -1.0 and sign(interval2) == 1.0 and abs(interval2) <= M3:
                return True
            else:
                return False
        return True

    def _is_octave_compensated(self, ctp_draft, idx):
        if idx >= self.end_idx[0] - 2 or ctp_draft[idx] == -1:
            return True
        interval1 = ctp_draft[idx + 1] - ctp_draft[idx]
        interval2 = ctp_draft[idx + 2] - ctp_draft[idx + 1]
        if self._is_melodic_leap_octave(ctp_draft, idx + 1):
            if self._is_leap_compensated(ctp_draft, idx + 1) and sign(interval1) != sign(interval2):
                return True
            else:
                return False
        else:
            return True

    def _is_chromatic_step(self, ctp_draft, idx):
        if idx >= self.end_idx[0] or ctp_draft[idx] == -1:
            return False
        if abs(ctp_draft[idx + 1] - ctp_draft[idx]) == 1 and ctp_draft[idx + 1] not in self.scale_pitches:
            return True
        return False

    def _is_repeating_pitches(self,ctp_draft,idx):
        if idx in self.end_idx:
            return False
        if ctp_draft[idx] == ctp_draft[idx + 1]:
            if self.ties[idx] == True:
                return False
            else:
                return True
        return False

    def _is_within_range_of_a_tenth(self, ctp_draft):
        if max(ctp_draft) - min(ctp_draft[1:]) >= Octave + M3:
            return False
        else:
            return True


    def _is_unique_climax(self, ctp_draft):
        # Unique climax that is different from the cantus firmus or with sufficient spacing
        climax = max(ctp_draft)
        climax_measure_idx = []
        for measure in range(len(self.ctp_in_measure)):
            if climax in self.ctp_in_measure[measure]:
                for i in range(self.ctp_in_measure[measure].count(climax)):
                    climax_measure_idx.append(measure)
        if len(climax_measure_idx) == 1:
            if self.short_cf.index(max(self.short_cf)) == climax_measure_idx[0]:
                return False
            else:
                return True
        for i in range(len(climax_measure_idx)-1):
            if abs(climax_measure_idx[i] - climax_measure_idx[i+1]) < 4:
                return False
            if self.short_cf.index(max(self.short_cf)) == climax_measure_idx[i]:
                return False
        return True

    """ SECOND SPECIES """
    def _is_motivic_repetitions(self,ctp_draft,idx):
        if idx >= len(ctp_draft)-3:
            return False
        if ctp_draft[idx:idx + 2] == ctp_draft[idx + 2:idx + 4]:
            return True
        return False

    def _melodic_rules(self, ctp_draft):
        penalty = 0
        # Index based rules
        if SPECIES[self.species] >= 1: # valid melodic rules for each species
            for i in range(len(ctp_draft)):
                if self._is_melodic_leap_too_large(ctp_draft, i):
                    self.ctp_errors.append("Too large leap!")
                    penalty += 100
                    self.weighted_indices[i] += 4
                if self._is_melodic_leap_octave(ctp_draft, i):
                    self.ctp_errors.append("Octave leap!")
                    penalty += 25
                    self.weighted_indices[i] += 1
                if not self._is_leap_compensated(ctp_draft, i):
                    self.ctp_errors.append("Leap not compensated!")
                    penalty += 50
                    self.weighted_indices[i] += 2
                if not self._is_octave_compensated(ctp_draft, i):
                    self.ctp_errors.append("Octave not compensated!")
                    penalty += 25
                    self.weighted_indices[i] += 1
                if self._is_successive_same_direction_leaps(ctp_draft, i):
                    self.ctp_errors.append("Successive Leaps in same direction!")
                    penalty += 25
                    self.weighted_indices[i] += 1
                    if not self._is_successive_leaps_valid(ctp_draft, i):
                        self.ctp_errors.append("Successive leaps strictly not valid!")
                        penalty += 100
                        self.weighted_indices[i] += 4
                if self._is_chromatic_step(ctp_draft, i):
                    self.ctp_errors.append("Chromatic movement!")
                    penalty += 100
                    self.weighted_indices[i] += 4
                if self._is_repeating_pitches(ctp_draft,i):
                    self.ctp_errors.append("Repeats pitches!")
                    penalty += 100
                    self.weighted_indices[i] += 1
            # Global rules
            if not self._is_within_range_of_a_tenth(ctp_draft):
                self.ctp_errors.append("Exceeds the range of a tenth!")
                penalty += 50
            if not self._is_unique_climax(ctp_draft):
                self.ctp_errors.append("No unique climax or at same position as other voices!")
                penalty += 100
        if SPECIES[self.species] >= 2:
            for i in range(len(ctp_draft)):
                if self._is_motivic_repetitions(ctp_draft,i):
                    self.ctp_errors.append("Motivic repetitions!")
                    penalty += 100
        return penalty

    """ VOICE INDEPENDENCE RULES """

    def _is_perfect_interval_properly_approached(self, upper_voice, lower_voice, idx):
        if idx in self.start_idx or idx in self.end_idx or idx not in self.measure_idx:  # the start and end notes is allowed to be perfect
            return True
        if upper_voice[idx] - lower_voice[idx] in self.perfect_intervals:
            if self.motion(idx, upper_voice, lower_voice) not in ["oblique", "contrary"]:
                return False
            if self._is_large_leap(upper_voice, idx - 1) or self._is_large_leap(lower_voice, idx - 1):
                if upper_voice[idx] - lower_voice[idx] == Octave:
                    if self.motion(idx, upper_voice, lower_voice) == "oblique" or idx == len(upper_voice) - 1:
                        return True
                else:
                    return False
        return True

    def _is_valid_consecutive_perfect_intervals(self, upper_voice, lower_voice, idx):
        if upper_voice[idx] == -1 or lower_voice[idx] == -1 or idx in self.end_idx or idx not in self.measure_idx:
            return True
        harm_int1 = upper_voice[idx] - lower_voice[idx]
        harm_int2 = upper_voice[idx + 1] - lower_voice[idx + 1]
        if harm_int1 in self.perfect_intervals and harm_int2 in self.perfect_intervals:
            if self._is_step(upper_voice, idx) or self._is_step(lower_voice, idx):
                return True
            else:
                return False
        return True

    def _is_parallel_fourths(self, upper_voice, lower_voice, idx):
        if upper_voice[idx] == -1 or lower_voice[idx] == -1 or idx == self.end_idx[0]:
            return False
        if self.motion(idx, upper_voice, lower_voice) == "parallel" and upper_voice[idx] - lower_voice[idx] == P4:
            return True
        return False

    def _is_voice_overlapping(self, upper_voice, lower_voice, idx):
        if upper_voice[idx] == -1 or lower_voice[idx] == -1:
            return False
        if idx < self.end_idx[0] and lower_voice[idx + 1] >= upper_voice[idx]:
            return True
        return False

    def _is_voice_crossing(self, upper_voice, lower_voice, idx):
        if upper_voice[idx] == -1 or lower_voice[idx] == -1:
            return False
        if upper_voice[idx] - lower_voice[idx] < 0:
            return True
        return False

    def _is_contrary_motion(self, upper_voice, lower_voice, idx):
        if self.motion(idx, upper_voice, lower_voice) == "contrary":
            return True
        else:
            return False

    def _is_valid_number_of_consecutive_intervals(self, upper_voice, lower_voice):
        valid = True
        for i in range(len(lower_voice) - 3):
            i1 = self._get_interval_degree(upper_voice[i] - lower_voice[i])
            i2 = self._get_interval_degree(upper_voice[i + 1] - lower_voice[i + 1])
            i3 = self._get_interval_degree(upper_voice[i + 2] - lower_voice[i + 2])
            i4 = self._get_interval_degree(upper_voice[i + 3] - lower_voice[i + 3])
            if i1 == i2 == i3 == i4:
                valid = False
        return valid

    def _is_unisons_between_terminals(self, ctp):
        if SPECIES[self.species] in [3,5]:
            return 0
        return ctp[1:-1].count(self.cf_tonic)

    """ SECOND SPECIES"""
    def _is_parallel_perfects_on_downbeats(self,ctp_draft, upper_voice, lower_voice):
        if SPECIES[self.species] == 2 or SPECIES[self.species] == 4:
            db = self.get_downbeats()
        else:
            db = self.get_firstbeats()
        for i in range(len(db) - 1):
            interval1 = upper_voice[db[i]] - lower_voice[db[i]]
            interval2 = upper_voice[db[i + 1]] - lower_voice[db[i + 1]]
            if interval1 == interval2 and interval1 in self.perfect_intervals:
                # consecutive perfects on downbeats
                if upper_voice[db[i + 1]] - upper_voice[db[i]] == lower_voice[db[i + 1]] - lower_voice[db[i]]:
                    # consecutive and parallel
                    if ctp_draft[db[i]] - ctp_draft[db[i] + 1] > M3:
                        return False
                    else:
                        return True
                return False
        return False

    def _voice_independence_rules(self, ctp_draft, cf_notes):
        if self.ctp_position == "above":
            upper_voice = ctp_draft
            lower_voice = cf_notes
        else:
            upper_voice = cf_notes
            lower_voice = ctp_draft
        penalty = 0
        # Index based rules
        if SPECIES[self.species] >= 1: # valid rules for each species
            for i in range(len(ctp_draft)):
                if not self._is_perfect_interval_properly_approached(upper_voice, lower_voice, i):
                    self.ctp_errors.append("Perfect interval not properly approached!")
                    penalty += 100
                    self.weighted_indices[i] += 4
                if not self._is_valid_consecutive_perfect_intervals(upper_voice, lower_voice, i):
                    self.ctp_errors.append("Consecutive perfect intervals, but they are not valid!")
                    penalty += 100
                    self.weighted_indices[i] += 4
                if self._is_parallel_fourths(upper_voice, lower_voice, i):
                    self.ctp_errors.append("Parallel fourths!")
                    penalty += 50
                    self.weighted_indices[i] += 2
                if self._is_voice_overlapping(upper_voice, lower_voice, i):
                    self.ctp_errors.append("Voice Overlapping!")
                    penalty += 100
                    self.weighted_indices[i] += 4
                if self._is_voice_crossing(upper_voice, lower_voice, i):
                    self.ctp_errors.append("Voice crossing!")
                    penalty += 50
                    self.weighted_indices[i] += 2
                if self._is_contrary_motion(upper_voice, lower_voice, i):
                    # This not not a severe violation, but more of a preference to avoid similar motion
                    penalty += 5
            # Global rules
            if not self._is_valid_number_of_consecutive_intervals(upper_voice, lower_voice):
                self.ctp_errors.append("Too many consecutive intervals!")
                penalty += 100
            if self._is_unisons_between_terminals(ctp_draft) > 0:
                self.ctp_errors.append("Unison between terminals!")
                penalty += 50 * self._is_unisons_between_terminals(ctp_draft)
        if SPECIES[self.species] >= 2:
            if self._is_parallel_perfects_on_downbeats(ctp_draft, upper_voice, lower_voice):
                self.ctp_errors.append("Parallel perfect intervals on downbeats!")
                penalty += 100
        return penalty

    """ DISSONANT RULES"""
    def _is_dissonant_interval(self,upper_voice,lower_voice,idx):
        if upper_voice[idx]-lower_voice[idx] in self.dissonant_intervals:
            return True
        else:
            return False
    def _tied_note_properly_resolved(self,cf_notes,ctp_draft):
        penalty = 0
        if self.ctp_position == "above":
            upper = ctp_draft
            lower = cf_notes
        else:
            upper = cf_notes
            lower = ctp_draft
        for i in range(len(ctp_draft)-1):
            if i in self.start_idx or i in self.end_idx:
                penalty += 0
            elif i in self.get_downbeats():
                if  upper[i]-lower[i] in self.harmonic_consonances:
                    penalty += 0
                else:
                    if (ctp_draft[i+1] - ctp_draft[i]) < 0 and self._is_step(ctp_draft,i):
                        penalty += 0
                    else:
                        self.ctp_errors.append("Dissonance not properly resolved")
                        penalty += 100
        return penalty

    " Fifth species"
    def _is_eight_note_handled(self,idx,ctp_draft):
        if idx in self.start_idx or idx in self.end_idx:
            return True
        if self.ctp_flat_rhythm[idx] != 1:
            # not eight_note
            return True
        if self._is_step(ctp_draft,idx) and self._is_step(ctp_draft,idx-1):
            # The eight note is not approached or left by step
            return True
        else:
            return False

    def _is_dissonance_properly_left_and_approached(self,idx,ctp_draft):
        current_note = ctp_draft[idx]
        prev_note = ctp_draft[idx-1]
        next_note = ctp_draft[idx+1]
        if abs(next_note-current_note) <= M2 and abs(current_note-prev_note) <= M2:
            if SPECIES[self.species] in [5]:
                return True
            if sign(next_note-current_note) == sign(next_note-current_note):
                return True
            else:
                return False
        else:
            return False

    def _dissonance_handling(self, cf_notes, ctp_draft):
        penalty = 0
        if SPECIES[self.species] == 1:
            # In first species there is no dissonance, so the allowed harmonic intervals are consonances
            return penalty
        if self.ctp_position == "above":
            upper = ctp_draft
            lower = cf_notes
        else:
            upper = cf_notes
            lower = ctp_draft
        if SPECIES[self.species] in [2,3,5]: # In second species dissonances are allowed if they are approached and left by step
            for i in range(1, len(ctp_draft)-1):
                if SPECIES[self.species] == 3 and self._is_cambiata(i,cf_notes,ctp_draft):
                    # allowed
                    penalty += 0
                elif self._is_dissonant_interval(upper,lower,i):
                    if not self._is_dissonance_properly_left_and_approached(i,ctp_draft):
                        self.ctp_errors.append("Dissonance not properly left or approached!")
                        penalty += 100
        if SPECIES[self.species] == 5:
            for i in range(1,len(ctp_draft)-1):
                if not self._is_eight_note_handled(i,ctp_draft):
                    self.ctp_errors.append("eight notes not properly handled!")
                    penalty += 100
        if SPECIES[self.species] in [4,5]:
            penalty += self._tied_note_properly_resolved(cf_notes,ctp_draft)

        return penalty

    def _is_cambiata(self,idx, cf_notes,ctp_draft):
        if idx % 4 == 0:
            notes = [ctp_draft[idx+i] for i in range(4)]
            cf = cf_notes[idx]
            if self.ctp_position == "above":
                intervals = [note - cf for note in notes]
                interval_degree = []
                for i in intervals:
                    interval_degree.append(self._get_interval_degree(i))
                if interval_degree == ["octave","seventh","fifth","sixth"]:
                    return True
                if interval_degree == ["sixth","d5","third","fourth"]:
                    return True
            else:
                intervals = [cf-note for note in notes]
                interval_degree = []
                for i in intervals:
                    interval_degree.append(self._get_interval_degree(i))
                if interval_degree == ["third","fourth","sixth","fifth"]:
                    return True
        return False



    """ HARMONIC RULES """

    def _is_valid_terminals(self, ctp_draft, cf_notes):
        # check start and end pitches and see if they are valid
        # must begin and end with perfect consonances (octaves, fifths or unison)
        # Octaves or unisons preferred at the end (i.e. perfect fifth not allowed)
        # if below, the start and end must be the octave the cf
        if ctp_draft[0] == -1:
            idx = 1
        else:
            idx = 0
        if self.ctp_position == "above":
            if (ctp_draft[idx] - cf_notes[idx] not in [Unison, P5, Octave]) or (
                    ctp_draft[-1] - cf_notes[-1] not in [Unison, Octave]):
                return False
            else:
                return True
        else:
            if (cf_notes[idx] - ctp_draft[idx] not in [Unison, Octave]) or (
                    cf_notes[-1] - ctp_draft[-1] not in [Unison, Octave]):
                return False
            else:
                return True

    def _no_outlined_tritone(self, ctp_draft):
        outline_idx = [0]
        outline_intervals = []
        not_allowed_intervals = [Tritone]
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

    def _harmonic_rules(self, ctp_draft, cf_notes):
        penalty = 0
        if SPECIES[self.species] >= 1: # valid harmonic rules for each species
            if not self._is_valid_terminals(ctp_draft, cf_notes):
                self.ctp_errors.append("Terminals not valid!")
                penalty += 100
        if SPECIES[self.species] in [3,5]:
            if not self._no_outlined_tritone(ctp_draft):
                self.ctp_errors.append("Outlined dissonant interval!")
                penalty += 50
        return penalty

    """ TOTAL PENALTY"""

    def total_penalty(self, ctp_draft, cf_notes):
        penalty = 0
        self.ctp_errors = []
        penalty += self._melodic_rules(ctp_draft)
        penalty += self._voice_independence_rules(ctp_draft, cf_notes)
        penalty += self._dissonance_handling(cf_notes, ctp_draft)
        penalty += self._harmonic_rules(ctp_draft, cf_notes)
        return penalty

    def get_penalty(self):
        penalty = self.total_penalty(self.ctp,self.cf_notes)
        return penalty

    def get_errors(self):
        return self.ctp_errors
    def get_weighted_indices(self):
        return dict(sorted(self.weighted_indices.items(),reverse=True, key=lambda item: item[1]))