import argparse
import os
import json
import random
import math
from itertools import product
from collections import defaultdict
import copy


YAHTZEE_CHOICES_PATH = "choices.json"
YAHTZEE_EV_PATH = "ev.json"
YAHTZEE_EV_FULL_PATH = "ev_full.json"
YAHTZEE_PROBABILITIES_PATH = "probabilities.json"
reroll_cache = {}
UPPER_SECTION_OPTIONS = ["ones", "twos", "threes", "fours", "fives", "sixes"]
LOWER_SECTION_OPTIONS = ["3_of_a_kind", "4_of_a_kind", "full_house", "small_straight", "large_straight", "yahtzee", "chance"]
UPPER_SECTION_OPTIONS_SET = set(["ones", "twos", "threes", "fours", "fives", "sixes"])
ALL_OPTIONS_SET = set(UPPER_SECTION_OPTIONS + LOWER_SECTION_OPTIONS)
UPPER_FACE_VALUE = {
    "ones": 1, "twos": 2, "threes": 3,
    "fours": 4, "fives": 5, "sixes": 6
}

def display_table():
    if os.path.exists(YAHTZEE_CHOICES_PATH):
        with open(YAHTZEE_CHOICES_PATH) as f:
            data = json.load(f)
            items = data.items()
            print("------------------------")
            for item in items:
                filler_key = len("small_straight") - len(item[0])
                filler_key_str_l = " " * (filler_key // 2)
                filler_key_str_r = " " * ((filler_key + 1) // 2)

                value = str(item[1])
                if value == "None":
                    value = ""
                filler_value = len("999") - len(value)
                # print(value, filler_value)
                filler_val_str_l = " " * (filler_value // 2)
                filler_val_str_r = " " * ((filler_value + 1) // 2)
                print(f"| {filler_key_str_l}{item[0]}{filler_key_str_r} | {filler_val_str_l}{value}{filler_val_str_r} |")
                #print("------------------------")
            print("------------------------")

def roll():
    rolls = []
    for i in range(5):
        rolls.append(random.randint(1, 6))
    return rolls

def build_baseline_ev(cache):
    baseline_ev = {}
    empty_counts = (0, 0, 0, 0, 0, 0)

    for category in ALL_OPTIONS_SET:
        baseline_ev[category] = ev_category_full(
            empty_counts,
            rolls_left=2,
            category=category,
            evs=cache,
            upper_sum=0
        )

    return baseline_ev

def suggest_keep_die_full(
    rolls,
    roll_num,
    remaining_options,
    upper_sum
):
    counts = [0] * 6
    for r in rolls:
        counts[r - 1] += 1

    rolls_left = 3 - roll_num
    best_ev = -1e9
    best_keep = None

    if os.path.exists(YAHTZEE_EV_FULL_PATH):
        with open(YAHTZEE_EV_FULL_PATH) as f:
            cache = json.load(f)
    else:
        cache = {}

    baseline_ev = build_baseline_ev(cache)

    for keep in all_sub_multisets(counts):
        m = 5 - sum(keep)
        ev_keep = 0.0

        for outcome, p in reroll_outcomes(m):
            next_counts = tuple(keep[i] + outcome[i] for i in range(6))

            best_cat_ev = -1e9
            for category in remaining_options:
                cat_ev = ev_category_full(
                    next_counts,
                    rolls_left - 1,
                    category,
                    cache,
                    upper_sum
                )

                # regret vs baseline
                cat_ev -= baseline_ev[category]

                best_cat_ev = max(best_cat_ev, cat_ev)

            ev_keep += p * best_cat_ev

        if ev_keep > best_ev:
            best_ev = ev_keep
            best_keep = keep


    save_cache(cache)
    return keep_indices_from_counts(rolls, best_keep)

def suggest_category_choice(rolls, remaining_options, upper_sum):
    """Suggests the best category to use for scoring based on current rolls."""
    counts = [0] * 6
    for r in rolls:
        counts[r - 1] += 1
    counts = tuple(counts)

    # Load cache
    if os.path.exists(YAHTZEE_EV_FULL_PATH):
        with open(YAHTZEE_EV_FULL_PATH) as f:
            cache = json.load(f)
    else:
        cache = {}

    # Build baseline EVs
    baseline_ev = build_baseline_ev(cache)

    best_category = None
    best_value = -1e9

    for category in remaining_options:
        # Calculate actual score for this roll
        actual_score = score_category(counts, category)

        # Add bonus if applicable
        if category in UPPER_SECTION_OPTIONS_SET:
            new_upper_sum = upper_sum + actual_score
            if upper_sum < 63 and new_upper_sum >= 63:
                actual_score += 35  # Bonus!

        # Calculate regret (how much better than baseline)
        regret = actual_score - baseline_ev[category]

        if regret > best_value:
            best_value = regret
            best_category = category

    return best_category, best_value

def suggest_keep_die(rolls, roll_num, remaining_options):
    roll_counts = [0] * 6
    for r in rolls:
        roll_counts[r - 1] += 1

    rolls_left = 3 - roll_num
    best_ev = -1
    best_keep = None

    baseline_ev = {}
    for category in ALL_OPTIONS_SET:
        baseline_ev[category] = ev_category((0, 0, 0, 0, 0, 0), 2, category)

    for keep in all_sub_multisets(roll_counts):
        m = 5 - sum(keep)
        ev_keep = 0.0

        for outcome, p in reroll_outcomes(m):
            next_counts = tuple(keep[i] + outcome[i] for i in range(6))

            best_cat_ev = 0.0
            for category in remaining_options:
                best_cat_ev = max(
                    best_cat_ev,
                    ev_category(next_counts, rolls_left - 1, category) - baseline_ev[category]
                )

            ev_keep += p * best_cat_ev

        if ev_keep > best_ev:
            best_ev = ev_keep
            best_keep = keep
    #print(best_keep)

    return keep_indices_from_counts(rolls, best_keep)


def keep_indices_from_counts(rolls, keep_counts):
    keep = []
    needed = keep_counts.copy()

    for i, r in enumerate(rolls):
        idx = r - 1
        if needed[idx] > 0:
            keep.append(i)
            needed[idx] -= 1

    return keep

def prob_distribution(roll_num, die):
    return None

def prob_category(roll_counts, rolls_left, category):
    if os.path.exists(YAHTZEE_CHOICES_PATH):
        with open(YAHTZEE_CHOICES_PATH) as f:
            probs = json.load(f)
    else:
        os.makedirs(os.path.dirname(YAHTZEE_CHOICES_PATH) or ".", exist_ok=True)
        probs = {}
    roll_count_str = "".join(roll_counts)
    count_str = f"{roll_count_str}, {rolls_left}"
    
    if count_str in probs:
        return probs[roll_count_str]
    if rolls_left == 0 and lower_category_satisfied(roll_counts, category):
        return 1.0
    if rolls_left == 0:
        return 0.0
    
    best_prob = 0.0
    for keep in all_sub_multisets(roll_counts):
        m = 5 - sum(keep)
        prob = 0.0 

        for outcome, p_outcome in reroll_outcomes(m):
            #p_outcome = multinomial_prob(outcome, m)
            next_counts = keep + outcome

            prob += p_outcome * prob_category(next_counts, rolls_left - 1, category)

        best_prob = max(best_prob, prob)
    probs[count_str] = best_prob
    with open(YAHTZEE_CHOICES_PATH, "w") as f:
        json.dump(probs, f, indent=2)
    return best_prob


def ev_category_full(counts, rolls_left, category, evs, upper_sum=0):
    key = f"{tuple(counts)},{rolls_left},{category},{upper_sum}"

    #if os.path.exists(YAHTZEE_EV_FULL_PATH):
    #    with open(YAHTZEE_EV_FULL_PATH) as f:
    #        cache = json.load(f)
    #else:
    #    cache = {}

    if key in evs:
        return evs[key]

    if rolls_left == 0:
        val = score_category(counts, category)

        # Add bonus if this upper category completes the 63-point threshold
        if category in UPPER_SECTION_OPTIONS_SET:
            new_upper_sum = upper_sum + val
            if upper_sum < 63 and new_upper_sum >= 63:
                val += 35  # Bonus awarded!

        evs[key] = val
        #with open(YAHTZEE_EV_FULL_PATH, "w") as f:
        #    json.dump(evs, f)
        return val

    best_ev = 0.0
    for keep in all_sub_multisets(counts):
        m = 5 - sum(keep)
        ev = 0.0

        for outcome, p in reroll_outcomes(m):
            next_counts = tuple(keep[i] + outcome[i] for i in range(6))
            ev += p * ev_category_full(next_counts, rolls_left - 1, category, evs, upper_sum)

        best_ev = max(best_ev, ev)

    evs[key] = best_ev
    #with open(YAHTZEE_EV_PATH, "w") as f:
    #    json.dump(evs, f)

    return best_ev

def save_cache(cache):
    with open(YAHTZEE_EV_FULL_PATH, "w") as f:
        json.dump(cache, f, indent=2)

def ev_category(roll_counts, rolls_left, category):
    if os.path.exists(YAHTZEE_EV_PATH):
        with open(YAHTZEE_EV_PATH) as f:
            evs = json.load(f)
    else:
        evs = {}

    key = f"{tuple(roll_counts)},{rolls_left},{category}"
    if key in evs:
        return evs[key]

    if rolls_left == 0:
        return score_category(roll_counts, category)

    best_ev = 0.0

    for keep in all_sub_multisets(roll_counts):
        m = 5 - sum(keep)
        ev = 0.0

        for outcome, p in reroll_outcomes(m):
            next_counts = tuple(keep[i] + outcome[i] for i in range(6))
            ev += p * ev_category(next_counts, rolls_left - 1, category)

        best_ev = max(best_ev, ev)

    evs[key] = best_ev
    with open(YAHTZEE_EV_PATH, "w") as f:
        json.dump(evs, f, indent=2)

    return best_ev


def score_category(roll_counts, category):
    if category == "yahtzee":
        return 50 if max(roll_counts) == 5 else 0
    if category == "full_house":
        return 25 if 3 in set(roll_counts) and 2 in set(roll_counts) else 0
    if category == "small_straight":
        return 30 if get_longest_streak(roll_counts) >= 4 else 0
    if category == "large_straight":
        return 40 if get_longest_streak(roll_counts) == 5 else 0
    if category == "chance" or (category == "3_of_a_kind" and max(roll_counts) >= 3) or (category == "4_of_a_kind" and max(roll_counts) >= 4):
        output = 0
        for i in range(len(roll_counts)):
            output += roll_counts[i] * (i + 1)
        return output
    if category in UPPER_SECTION_OPTIONS_SET:
        for i in range(len(UPPER_SECTION_OPTIONS)):
            if category == UPPER_SECTION_OPTIONS[i]:
                return roll_counts[i] * (i + 1)
    return 0
            
            
def all_sub_multisets(roll_counts):
    result = []
    for k0 in range(roll_counts[0] + 1):
        for k1 in range(roll_counts[1] + 1):
            for k2 in range(roll_counts[2] + 1):
                for k3 in range(roll_counts[3] + 1):
                    for k4 in range(roll_counts[4] + 1):
                        for k5 in range(roll_counts[5] + 1):
                            result.append([k0, k1, k2, k3, k4, k5])
    return result

def reroll_outcomes(m):
    if m in reroll_cache:
        return reroll_cache[m]

    outcome_counts = defaultdict(int)

    for seq in product(range(6), repeat=m):
        counts = [0] * 6
        for face in seq:
            counts[face] += 1
        outcome_counts[tuple(counts)] += 1

    total = 6 ** m
    result = [
        (counts, freq / total)
        for counts, freq in outcome_counts.items()
    ]

    reroll_cache[m] = result
    return result

def lower_category_satisfied(roll_counts, category):
    if category == "yahtzee" and max(roll_counts) == 5:
        return True
    if category == "4_of_a_kind" and max(roll_counts) >= 4:
        return True
    if category == "3_of_a_kind" and max(roll_counts) >= 3:
        return True
    if category == "full_house" and 3 in set(roll_counts) and 2 in set(roll_counts):
        return True
    if category == "small_straight" or category == "large_straight":
        longest_streak = get_longest_streak(roll_counts)
        if (category == "small_straight" and longest_streak >= 4) or (category == "large_straight" and longest_streak == 5):
            return True
    if category == "chance":
        return True
    return False
    
def get_longest_streak(roll_counts):
    longest_streak = 0
    curr_streak = 0
    for count in roll_counts:
        if count > 0:
            curr_streak += 1
            longest_streak = max(longest_streak, curr_streak)
        else:
            curr_streak = 0
    return longest_streak

def multinomial_prob(outcome):
    m = sum(outcome)
    denom = 1
    for x in outcome:
        denom *= math.factorial(x)
    return math.factorial(m) / denom * (1/6)**m

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="My command-line tool")
    parser.add_argument("args", nargs="*", help="Any number of arguments")

    args = parser.parse_args()
    arguments = args.args
    roll_number = int(arguments[0])
display_table()