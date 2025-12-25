class Table:
    def __init__(self):
        self.table = {
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
            "yahtzee": None
        }

    def display(self):
        items = list(self.table.items())
        print("------------------------------")
        for i in range(len(items)):
            filler_key = len("small_straight") - len(items[i][0])
            filler_key_str_l = " " * (filler_key // 2)
            filler_key_str_r = " " * ((filler_key + 1) // 2)

            value = str(items[i][1])
            if value == "None":
                value = ""
            filler_value = len("999") - len(value)
            filler_val_str_l = " " * (filler_value // 2)
            filler_val_str_r = " " * ((filler_value + 1) // 2)

            if i < 9:
                index_str_r = " "
            else:
                index_str_r = ""
            print(f"|  {i + 1}{index_str_r} | {filler_key_str_l}{items[i][0]}{filler_key_str_r} | {filler_val_str_l}{value}{filler_val_str_r} |")
        print("------------------------------")