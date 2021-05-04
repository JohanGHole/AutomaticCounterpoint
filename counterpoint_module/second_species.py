"""" Second species counterpoint
TODO:
    - Generate a first species counterpoint
    - double the number of notes and split the note length in two
    - for weak beats, check for changes. No need to change the strong-beats since these are already checked
    - End note is a whole note
    - Start may be a rest
    - only dissonance if approached and left by melodic step. Else: consonance


"""
from counterpoint_module.first_species import *

class SecondSpecies(FirstSpecies):
    def __init__(self,cf,ctp_position = "above"):
        super(SecondSpecies, self).__init__(cf,ctp_position)
        self.generate_ctp()
        print(self.melody_rhythm)
        self._expand_ctp()
        self.cf = cf
        self.expanded_cf = [item for item in self.cf.melody for repetitions in range(2)]
        print("hello")

    """ MELODIC RULES """

    def _is_melodic_leap_too_large(self, ctp_draft, idx):
        if idx == len(ctp_draft) - 1:
            return False
        interval = ctp_draft[idx + 1] - ctp_draft[idx]
        if abs(interval) > P5:
            if sign(interval) == 1.0 and interval == m6:
                return False
            if abs(interval) == Octave:
                return False
            return True
        else:
            return False

    def _is_melodic_leap_octave(self, ctp_draft, idx):
        if idx == len(ctp_draft) - 1:
            return False
        interval = ctp_draft[idx + 1] - ctp_draft[idx]
        if abs(interval) == Octave:
            return True
        return False

    def _is_successive_same_direction_leaps(self, ctp_draft, idx):
        if idx >= len(ctp_draft) - 2:
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

    def _is_successive_leaps_valid(self, ctp_draft, idx):
        if idx >= len(ctp_draft) - 2:
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

    def _is_leap_compensated(self, ctp_draft, idx):
        if idx >= len(ctp_draft) - 2:
            return True
        interval1 = ctp_draft[idx + 1] - ctp_draft[idx]
        interval2 = ctp_draft[idx + 2] - ctp_draft[idx + 1]
        if abs(interval1) >= P5:
            if sign(interval1) == 1.0 and sign(interval2) == -1.0 and abs(interval2) <= M2:
                return True
            elif sign(interval1) == -1.0 and sign(interval2) == 1.0 and abs(interval2) <= M3:
                return True
            else:
                return False
        return True

    def _is_octave_compensated(self, ctp_draft, idx):
        if idx >= len(ctp_draft) - 3:
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

    def _is_within_range_of_a_tenth(self, ctp_draft):
        if max(ctp_draft) - min(ctp_draft) >= Octave + M3:
            return False
        else:
            return True

    def _is_repeating_pitches(self, ctp_draft):
        if self.ctp_position == "above":
            for i in range(len(ctp_draft) - 1):  # was 2
                if ctp_draft[i] == ctp_draft[i + 1]:  # == ctp_draft[i+2]:
                    return True
        else:
            for i in range(len(ctp_draft) - 1):
                if ctp_draft[i] == ctp_draft[i + 1]:
                    return True
        return False

    def _is_unique_climax(self, ctp_draft):
        # Unique climax that is different from the cantus firmus
        if ctp_draft.count(max(ctp_draft)) == 1 and (
                ctp_draft.index(max(ctp_draft)) != self.cf_notes.index(max(self.cf_notes))):
            return True
        else:
            return False

    def melodic_rules(self, ctp_draft):
        penalty = 0
        # Index based rules
        for i in range(len(ctp_draft)):
            if self._is_melodic_leap_too_large(ctp_draft, i):
                self.ctp_errors.append("Too large leap!")
                self.ctp_weights[i] += 4
                penalty += 100
            if self._is_melodic_leap_octave(ctp_draft, i):
                self.ctp_errors.append("Octave leap!")
                self.ctp_weights[i] += 2
                penalty += 25
            if not self._is_leap_compensated(ctp_draft, i):
                self.ctp_errors.append("Leap not compensated!")
                self.ctp_weights[i] += 2
                penalty += 25
            if not self._is_octave_compensated(ctp_draft, i):
                self.ctp_errors.append("Octave not compensated!")
                self.ctp_weights[i] += 2
                penalty += 25
            if self._is_successive_same_direction_leaps(ctp_draft, i):
                self.ctp_errors.append("Successive Leaps in same direction!")
                self.ctp_weights[i] += 1
                penalty += 10
                if not self._is_successive_leaps_valid(ctp_draft, i):
                    self.ctp_errors.append("Successive leaps strictly not valid!")
                    self.ctp_weights[i] += 4
                    penalty += 100
        # Global rules
        if not self._is_within_range_of_a_tenth(ctp_draft):
            self.ctp_errors.append("Exceeds the range of a tenth!")
            penalty += 100
        if self._is_repeating_pitches(ctp_draft):
            self.ctp_errors.append("Repeats pitches!")
            penalty += 75
        if not self._is_unique_climax(ctp_draft):
            self.ctp_errors.append("No unique climax or at same position as other voices!")
            penalty += 100
        return penalty

    """ RHYTHMIC RULES """

    def get_rhythm(self):
        "Voices all move together in the same rhythm as the cantus firmus."
        return [8] * len(self.cf_notes)

    """ VOICE INDEPENDENCE RULES """

    def _is_perfect_interval_properly_approached(self, upper_voice, lower_voice, idx):
        if idx == 0:  # the start interval MUST be a perfect interval and is therefore allowed
            return True
        if upper_voice[idx] - lower_voice[idx] in self.perfect_intervals:
            if self._motion(idx, upper_voice, lower_voice) not in ["oblique", "contrary"]:
                return False
            if self._is_large_leap(upper_voice, idx - 1) or self._is_large_leap(lower_voice, idx - 1):
                if upper_voice[idx] - lower_voice[idx] == Octave:
                    if self._motion(idx, upper_voice, lower_voice) == "oblique" or idx == len(upper_voice) - 1:
                        return True
                else:
                    return False
        return True

    def _is_valid_consecutive_perfect_intervals(self, upper_voice, lower_voice, idx):
        if idx >= len(upper_voice) - 1:
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
        if idx == len(upper_voice) - 1:
            return False
        if self._motion(idx, upper_voice, lower_voice) == "parallel" and upper_voice[idx] - lower_voice[idx] == P4:
            return True
        return False

    def _is_voice_overlapping(self, upper_voice, lower_voice, idx):
        if idx < len(lower_voice) - 1 and lower_voice[idx + 1] >= upper_voice[idx]:
            return True
        return False

    def _is_voice_crossing(self, upper_voice, lower_voice, idx):
        if upper_voice[idx] - lower_voice[idx] < 0:
            return True
        return False

    def _is_contrary_motion(self, upper_voice, lower_voice, idx):
        if self._motion(idx, upper_voice, lower_voice) == "contrary":
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
        if self.cf_tonic in ctp[1:-1]:
            return True
        else:
            return False

    def voice_independence_rules(self, ctp_draft, cf_notes):
        if self.ctp_position == "above":
            upper_voice = ctp_draft
            lower_voice = cf_notes
        else:
            upper_voice = cf_notes
            lower_voice = ctp_draft
        penalty = 0
        # Index based rules
        for i in range(len(ctp_draft)):
            if not self._is_perfect_interval_properly_approached(upper_voice, lower_voice, i):
                self.ctp_errors.append("Perfect interval not properly approached!")
                self.ctp_weights[i] += 4
                penalty += 100
            if not self._is_valid_consecutive_perfect_intervals(upper_voice, lower_voice, i):
                self.ctp_errors.append("Consecutive perfect intervals, but they are not valid!")
                self.ctp_weights[i] += 4
                penalty += 100
            if self._is_parallel_fourths(upper_voice, lower_voice, i):
                self.ctp_errors.append("Parallel fourths!")
                self.ctp_weights[i] += 2
                penalty += 50
            if self._is_voice_overlapping(upper_voice, lower_voice, i):
                self.ctp_errors.append("Voice Overlapping!")
                self.ctp_weights[i] += 4
                penalty += 100
            if self._is_voice_crossing(upper_voice, lower_voice, i):
                self.ctp_errors.append("Voice crossing!")
                self.ctp_weights[i] += 2
                penalty += 50
            if self._is_contrary_motion(upper_voice, lower_voice, i):
                # This not not a severe violation, but more of a preference to avoid similar motion
                self.ctp_weights[i] += 1
                penalty += 10
        # Global rules
        if not self._is_valid_number_of_consecutive_intervals(upper_voice, lower_voice):
            self.ctp_errors.append("Too many consecutive intervals!")
            penalty += 100
        if self._is_unisons_between_terminals(ctp_draft):
            self.ctp_errors.append("Unison between terminals!")
            penalty += 50
        return penalty

    """ DISSONANT RULES"""

    def dissonant_rules(self, ctp_draft):
        # In first species there is no dissonance, so the allowed harmonic intervals are consonances
        return 0

    """ HARMONIC RULES """

    def _is_valid_terminals(self, ctp_draft, cf_notes):
        # check start and end pitches and see if they are valid
        # must begin and end with perfect consonances (octaves, fifths or unison)
        # Octaves or unisons preferred at the end (i.e. perfect fifth not allowed)
        # if below, the start and end must be the octave the cf
        if self.ctp_position == "above":
            if (ctp_draft[0] - cf_notes[0] not in [Unison, P5, Octave]) or (
                    ctp_draft[-1] - cf_notes[-1] not in [Unison, Octave]):
                return False
            else:
                return True
        else:
            if (cf_notes[0] - ctp_draft[0] not in [Unison, Octave]) or (
                    cf_notes[-1] - ctp_draft[-1] not in [Unison, Octave]):
                return False
            else:
                return True

    def _no_outlined_tritone(self, ctp_draft):
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

    def harmonic_rules(self, ctp_draft, cf_notes):
        penalty = 0
        if not self._is_valid_terminals(ctp_draft, cf_notes):
            self.ctp_errors.append("Terminals not valid!")
            penalty += 100
        if not self._no_outlined_tritone(ctp_draft):
            self.ctp_errors.append("Outlined dissonant interval!")
            penalty += 100
        return penalty

    """ TOTAL PENALTY"""

    def total_penalty(self, ctp_draft, cf_notes):
        penalty = 0
        penalty += self.melodic_rules(ctp_draft)
        penalty += self.voice_independence_rules(ctp_draft, cf_notes)
        penalty += self.dissonant_rules(ctp_draft)
        penalty += self.harmonic_rules(ctp_draft, cf_notes)
        return penalty

    """ HELP FUNCTIONS FOR INITIALIZING COUNTERPOINT"""

    def _start_notes(self):
        if self.ctp_position == "above":
            return [self.cf_tonic, self.cf_tonic + P5, self.cf_tonic + Octave]
        else:
            return [self.cf_tonic - Octave, self.cf_tonic]

    def _end_notes(self):
        if self.ctp_position == "above":
            return [self.cf_tonic, self.cf_tonic + Octave]
        else:
            return [self.cf_tonic, self.cf_tonic - Octave]

    def _penultimate_notes(self, cf_end):  # Bug in penultimate
        if self.ctp_position == "above":
            s = 1
        else:
            s = -1
        if self.cf_direction[-1] == 1.0:
            penultimate = cf_end + 2
        else:
            penultimate = cf_end - 1
        return [penultimate, penultimate + s * Octave]

    def get_harmonic_possibilities(self, cf_note):
        poss = []
        for interval in self.harmonic_consonances:
            if self.ctp_position == "above":
                if cf_note + interval in self.scale_pitches:
                    poss.append(cf_note + interval)
            else:
                if cf_note - interval in self.scale_pitches:
                    poss.append(cf_note - interval)
        return poss

    def _possible_notes(self):
        poss = [None for elem in self.cf_notes]
        for i in range(len(self.cf_notes)):
            if i == 0:
                poss[i] = self._start_notes()
            elif i == len(self.cf_notes) - 2:
                poss[i] = self._penultimate_notes(self.cf_notes[i + 1])
            elif i == len(self.cf_notes) - 1:
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
    def _expand_ctp(self):
        notes = self.ctp_notes
        rhythm = self.melody_rhythm
        rhythm = [4]*len(rhythm)*2
        print(rhythm)
        notes_expanded = []
        notes = [ item for item in notes for repetitions in range(2) ]
        print(notes)
        self.melody_rhythm = rhythm
        self.ctp_notes = notes
cf = Cantus_Firmus("C","major",bar_length=2)
cf.generate_cf()
ctp = SecondSpecies(cf,ctp_position="above")
print(ctp.ctp_notes)