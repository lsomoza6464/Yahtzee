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
        items = self.table.items()
        print("------------------------")
        for item in items:
            filler_key = len("small_straight") - len(item[0])
            filler_key_str_l = " " * (filler_key // 2)
            filler_key_str_r = " " * ((filler_key + 1) // 2)

            value = str(item[1])
            if value == "None":
                value = ""
            filler_value = len("999") - len(value)
            filler_val_str_l = " " * (filler_value // 2)
            filler_val_str_r = " " * ((filler_value + 1) // 2)
            print(f"| {filler_key_str_l}{item[0]}{filler_key_str_r} | {filler_val_str_l}{value}{filler_val_str_r} |")
        print("------------------------")