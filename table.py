import copy

UPPER_SECTION_OPTIONS = ["ones", "twos", "threes", "fours", "fives", "sixes"]
LOWER_SECTION_OPTIONS = ["3_of_a_kind", "4_of_a_kind", "full_house", "small_straight", "large_straight", "yahtzee", "chance"]
ALL_OPTIONS_SET = set(UPPER_SECTION_OPTIONS + LOWER_SECTION_OPTIONS)

class Table:
    def __init__(self):
        self.dict = {
            "ones": None,
            "twos": None,
            "threes": None,
            "fours": None,
            "fives": None,
            "sixes": None,
            "3_of_a_kind": None,
            "4_of_a_kind": None,
            "full_house": None,
            "small_straight": None,
            "large_straight": None,
            "yahtzee": None,
            "chance": None
        }
        self.mapping = {
            "ones": 0,
            "twos": 1,
            "threes": 2,
            "fours": 3,
            "fives": 4,
            "sixes": 5,
            "3_of_a_kind": 6,
            "4_of_a_kind": 7,
            "full_house": 8,
            "small_straight": 9,
            "large_straight": 10,
            "yahtzee": 11,
            "chance": 12,
            "3 of a kind": 6,
            "4 of a kind": 7,
            "full house": 8,
            "small straight": 9,
            "large straight": 10
        }
        self.reverse_mapping = {
            0: "ones",
            1: "twos",
            2: "threes",
            3: "fours",
            4: "fives",
            5: "sixes",
            6: "3_of_a_kind",
            7: "4_of_a_kind",
            8: "full_house",
            9: "small_straight",
            10: "large_straight",
            11: "yahtzee",
            12: "chance"
        }
        self.table = [["ones", None], ["twos", None], ["threes", None], ["fours", None], ["fives", None], ["sixes",None], ["3_of_a_kind", None], ["4_of_a_kind", None], ["full_house", None], ["small_straight", None], ["large_straight", None], ["yahtzee", None], ["chance", None]]
        self.options = copy.deepcopy(ALL_OPTIONS_SET)

    def display(self):
        #items = list(self.dict.items())
        print("------------------------------")
        for i in range(len(self.table)):
            filler_key = len("small_straight") - len(self.table[i][0])
            filler_key_str_l = " " * (filler_key // 2)
            filler_key_str_r = " " * ((filler_key + 1) // 2)

            value = str(self.table[i][1])
            if value == "None":
                value = ""
            filler_value = len("999") - len(value)
            filler_val_str_l = " " * (filler_value // 2)
            filler_val_str_r = " " * ((filler_value + 1) // 2)

            if i < 9:
                index_str_r = " "
            else:
                index_str_r = ""
            print(f"|  {i + 1}{index_str_r} | {filler_key_str_l}{self.table[i][0]}{filler_key_str_r} | {filler_val_str_l}{value}{filler_val_str_r} |")
        print("------------------------------")

    def add_selection(self, selection, rolls):
        if selection.isnumeric() and int(selection) >= 1 and int(selection) <= len(self.table):
            index = int(selection) - 1
        elif selection in self.mapping:
            index = self.mapping[selection]
        else:
            return ValueError("selection index not found")
        value = self.get_roll_value(index, rolls)
        self.table[index][1] = value
        #if self.reverse_mapping[index] == "yahtzee":
        #    self.options.add("yahtzee2")
        #if self.reverse_mapping[index] != "yahtzee2":
        #    self.options.remove(self.reverse_mapping[index])
        if self.reverse_mapping[index] != "yahtzee":
            self.options.remove(self.reverse_mapping[index])
    
    def yahtzee_found(self):
        if self.table[self.mapping["yahtzee"]][1] is not None:
            return True
        return False

    def get_roll_value(self, index, rolls):
        value = self.multi_yahtzee(index, rolls) # start value at the 100 of multi-yahtzee and add from there
        if not self.zero_score(index, rolls):
            if index < 6:
                for roll in rolls:
                    if roll == index + 1:
                        value += roll
            elif index == 6 or index == 7 or index == 12:
                value += sum(rolls)
            elif index == 8:
                value += 25
            elif index == 9:
                value += 30
            elif index == 10:
                value += 40
            elif index == 11:
                value += 50
        return value

    def zero_score(self, index, rolls): # checks if the rolls actually are valid for each requirements
        freqArr = [0] * 7
        for roll in rolls:
            freqArr[roll] += 1
        freqSet = set(freqArr)
        seq_length = self.len_longest_sequence(rolls)
        if (index == 6 and (3 not in freqSet and 4 not in freqSet and 5 not in freqSet)) or (index == 7 and (4 not in freqSet and 5 not in freqSet)) or (index == 8 and (3 not in freqSet or 2 not in freqSet)) or (index == 9 and seq_length < 4) or (index == 10 and seq_length < 5) or (index == 11 and 5 not in freqSet):
            return True
        return False
    
    def len_longest_sequence(self, rolls):
        seqSet = set(rolls)
        count = 0
        max_count = 0
        for i in range(1, 7):
            if i in seqSet:
                count += 1
            else:
                count = 0
            max_count = max(max_count, count)
        return max_count

    def multi_yahtzee(self, index, rolls):
        if self.table[11] is not None and len(set(rolls)) == 1 and index != 11:
            return 100
        return 0
    
    def check_selection(self, selection):
        if selection.isnumeric() and int(selection) >= 1 and int(selection) <= len(self.table):
            index = int(selection) - 1
        elif selection in self.mapping:
            index = self.mapping[selection]
        else:
            return "invalid"
        if self.table[index][1] is not None:
            return "taken"
        return index # kinda messy to return strings or ints
    
    def calculate_scores(self):
        score_arr = list(map(lambda x: x[1], self.table))
        true_score_arr = list(map(lambda x: x - 100 if x >= 100 else x, score_arr))
        upper_score = sum(score_arr[0:6])
        true_upper_score = sum(true_score_arr[0:6])
        if true_upper_score >= 63:
            upper_score += 35
            true_upper_score += 35
        lower_score = sum(score_arr[6:len(score_arr)])
        true_lower_score = sum(true_score_arr[6:len(true_score_arr)])
        return [upper_score + lower_score, true_upper_score + true_lower_score]