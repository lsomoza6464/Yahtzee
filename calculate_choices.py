import argparse
import os
import json
import random


YAHTZEE_CHOICES_PATH = "choices.json"

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="My command-line tool")
    parser.add_argument("args", nargs="*", help="Any number of arguments")

    args = parser.parse_args()
    arguments = args.args
    roll_number = int(arguments[0])
    display_table()