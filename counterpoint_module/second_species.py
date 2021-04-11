import math
from counterpoint_module.first_species import *

"""

TODO:
    add functionality for dissonance
    restructure such that similar rules as first species cpt is inherited and not restated
    
"""
def sign(x):
    return math.copysign(1, x)


def second_species_counterpoint(notes, tonic, voice_range, upper=True, verbose=False):
    # From cantus firmus:
    cf_melodic_intervals = [notes[i + 1] - notes[i] for i in range(len(notes) - 1)]
    directions = [sign(cf_melodic_intervals[i]) for i in range(len(cf_melodic_intervals))]
    perfect_intervals = [Unison, P5, Octave]

    # Counterpoint
    harmonic_intervals = [None for x in notes]
    possible_leaps = [m3, M3, P4, P5, m6, M6, Octave]
    if upper:
        consonant_intervals = [m3, M3, P5, m6, M6, Octave + M3, Octave + m3]
    else:
        consonant_intervals = [m3, M3, P4, m6, M6, Octave + M3, Octave + m3]
        consonant_intervals = [x * -1 for x in consonant_intervals]
    if upper:
        signum = 1
    else:
        signum = -1
    counterpoint_range = voice_range + signum

    counterpoint_range_note_numb = RANGES[counterpoint_range]

    # Strict Rules
    def get_start_possibilities():
        if upper:
            return [tonic + P5, tonic + Octave]
        else:
            return [tonic - Octave]

    def get_end_possibility():
        if upper:
            return [tonic + Octave]
        else:
            return [tonic - Octave]

    def get_leading_tone():
        # Rule 3
        if notes[-2] % Octave == (tonic % Octave + 2) % Octave:
            if upper:
                penultimate_note = tonic + 11
            else:
                penultimate_note = tonic - Octave - 1
        elif notes[-2] % Octave == (tonic % Octave + 11) % Octave:
            if upper:
                penultimate_note = tonic + Octave + 2
            else:
                penultimate_note = tonic - Octave + 2
        else:
            if verbose:
                print("FAIL: Rule 3 not satisfied")
                return
        return [penultimate_note]

    def get_consonant_possibilities(note):
        p = []
        for i in consonant_intervals:
            p.append(note + i)
        return p

    def check_accidentals(possibilities):
        p = possibilities.copy()
        for poss in p:
            if poss % Octave in SHARPS_IDX:
                possibilities.remove(poss)

    def get_melodic_intervals(possibilities, prev_note):
        """
        :param possibilities: list of possibilities in pitch values
        :param prev_note: previous note in the counterpoint melody
        :return: the melodic intervals
        """

        poss = possibilities.copy()
        return [p - prev_note for p in poss]

    def get_harmonic_intervals(possibilities, cf_note):
        if upper:
            return [p - cf_note for p in possibilities]
        else:
            return [cf_note - p for p in possibilities]

    # Checks for complete counterpoint

    def check_valid_melodic_outline(counterpoint):
        outline_idx = [0]
        outline_intervals = []
        not_allowed_intervals = [Tritone, M7]
        # mellom ytterkant og inn + endring innad
        dir = [sign(counterpoint[i + 1] - counterpoint[i]) for i in range(len(counterpoint) - 1)]
        for i in range(len(dir) - 1):
            if dir[i] != dir[i + 1]:
                outline_idx.append(i + 1)
        outline_idx.append(len(counterpoint) - 1)
        # Iterate over the outline indices and check if a tritone is found
        for i in range(len(outline_idx) - 1):
            outline_intervals.append(abs(counterpoint[outline_idx[i]] - counterpoint[outline_idx[i + 1]]))

        for interval in not_allowed_intervals:
            if interval in outline_intervals:
                return False

        return True

    def check_harmonic_motion(possibilities, prev_note, cf_note, index):
        # Removes the possibility of perfect harmonic intervals if the voices move in parallel motion
        melodic_intervals = get_melodic_intervals(possibilities, prev_note)
        harmonic_intervals = get_harmonic_intervals(possibilities, cf_note)
        p = possibilities.copy()
        if P4 in harmonic_intervals:
            possibilities.remove(p[harmonic_intervals.index(P4)])
        for i in range(len(p)):
            if directions[index] == sign(melodic_intervals[i]) and harmonic_intervals[i] in perfect_intervals:
                # Remove perfect consonants in parallel motion
                possibilities.remove(p[i])

    def check_leaps(possibilities, prev_note):
        melodic_intervals = get_melodic_intervals(possibilities, prev_note)
        p = possibilities.copy()
        for l in melodic_intervals:
            if l >= 3 and abs(l) not in possible_leaps:
                possibilities.remove(p[melodic_intervals.index(l)])

    def get_strict_possibilities(index, cp_notes):
        """
        :param index: int - index of cantus firmus to be harmonized
        :return poss: list of possible counterpoint tones
        """
        cf_note = notes[index]
        if index > 0:
            prev_note = cp_notes[index - 1]
        else:
            prev_note = None

        # Strict Rule nr 4
        if index == 0:
            poss = get_start_possibilities()
        elif index == len(notes) - 1:
            poss = get_end_possibility()

        # Strict rule nr 5
        else:
            # Rule nr 3
            poss = get_consonant_possibilities(cf_note)
            # rule nr 6
            check_harmonic_motion(poss, prev_note, cf_note, index)
            # Rule nr 7
            check_leaps(poss, prev_note)
            if get_leading_tone()[0] in poss and index == len(notes) - 2:
                poss = get_leading_tone()
        # Rule nr 2
        check_accidentals(poss)
        return poss

    def check_repeats(poss, cp_notes, index):
        possCopy = poss.copy()
        if index >= 2:
            for p in possCopy:
                if p == cp_notes[index - 1] == cp_notes[index - 2]:  # Three successive repeats of same note
                    poss.remove(p)

    def check_successive_leaps(poss, cp_notes, index, strict_factor):
        possCopy = poss.copy()
        if index < 2:  # Too early to check for successive leaps! No change is made
            return poss
        else:
            prev_interval = cp_notes[index - 1] - cp_notes[index - 2]
            print("Prev interval: ", prev_interval)
            if abs(prev_interval) >= 3:  # The prev interval was a leap
                for p in possCopy:
                    current_interval = p - cp_notes[index - 1]
                    print("current interval: ", current_interval)
                    if abs(current_interval) >= 3:  # two successive intervals!
                        # Rule 4
                        if sign(current_interval) != sign(
                                prev_interval):  # This last #Opposite direction and leap, not allowed
                            poss.remove(p)
                        # Rule 2
                        elif abs(current_interval) + abs(prev_interval) >= Octave:  # Then this
                            poss.remove(p)
                        # Rule 3

                        elif sign(current_interval) == sign(prev_interval) == 1.0:  # first to go
                            # Ascending. Prev_interval must be larger or equal to current_interval
                            if current_interval >= prev_interval:
                                poss.remove(p)
                        elif sign(current_interval) == sign(prev_interval) == -1.0:
                            if abs(prev_interval) >= abs(current_interval):
                                poss.remove(p)

    def get_soft_possibilities(poss, cp_notes, index, strict_factor=1.0):
        """
        :param poss: strict_possibilities
        :param index: current index of counterpoint construction
        :param strict_factor: a strict factor that controls how many of the checks to be included
        :return:
        """
        soft_poss = poss.copy()
        # Soft rule 1
        check_repeats(soft_poss, cp_notes, index)
        # Soft rule 2, 3 and 4
        check_successive_leaps(soft_poss, cp_notes, index, strict_factor)
        print("soft poss: ", soft_poss)
        return soft_poss

    def poss_is_empty(poss):
        return poss == []

    def no_possible_leading_tone(poss, i):
        return i == len(notes) - 2 and get_leading_tone()[0] not in poss

    def construct_counterpoint():
        """
        Constructs a counterpoint either above or below the given cantus firmus.
        The counterpoint must satisfy all of the strict rules of counterpoint.
        The counterpoint should satisfy as many of the soft rules of counterpoint as possible.

        :return cp_notes: list of counterpoint notes that satisfy as many of the
        """
        backTrack = False
        cp_poss = [None for x in notes]
        cp_notes = [None for x in notes]
        i = 0
        while i < len(notes):
            if backTrack:
                i -= 1
                cp_poss[i].remove(cp_notes[i])
                cp_notes[i] = None
                poss = cp_poss[i]
                backTrack = False
            else:
                poss = get_strict_possibilities(i, cp_notes)
                poss = get_soft_possibilities(poss, cp_notes, i)
                # print("poss after soft poss for idx "+str(i)+": ",poss)
            if poss_is_empty(poss) or no_possible_leading_tone(poss, i):
                backTrack = True

            else:
                cp_poss[i] = poss
                cp_notes[i] = rm.choice(poss)
                i += 1
        return cp_notes

    valid_outline = False
    # the construction is wrapped in strict global checkers that satisfy the strict rules must be satisfied. To avoid
    # modification of the constructed counterpoint, another call is made until all conditions are satisfied.
    while not valid_outline:
        cp_notes = construct_counterpoint()
        print("valid melodic outline? : ", check_valid_melodic_outline(cp_notes))
        if check_valid_melodic_outline(cp_notes):
            valid_outline = True
    print(cp_notes)
    return cp_notes