import argparse
import os
import json
import random
from table import Table


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

def roll(kept_rolls):
    for i in range(len(kept_rolls)):
        if kept_rolls[i] is None:
            kept_rolls[i] = random.randint(1, 6)
    return kept_rolls

def main():
    print("Welcome to Yahtzee")
    print("After each roll, you will be provided with the current turn and roll.")
    print("If you ever need help or instructions on the application, write 'help'.")
    print("If you ever need rules for Yahtzee, you can visit this site: ''website'' or write 'rules'.")
    #print("If you want to display the current table, write 'table'")
    #display_table()
    table = Table()
    for turn in range(1, 14):
        table.display()
        kept_rolls = [None] * 5
        for roll_num in range(1, 4):
            print(f"turn: {turn}")
            print(f"roll: {roll_num}")
            rolls = roll(kept_rolls)
            print(f"Your die results are: {rolls}")
            if roll_num < 3:
                keep_choice = input("Which numbers do you want to keep? (format is '01001' if you want to keep the second and fifth die): ")
            for i in range(len(keep_choice)):
                if keep_choice[i] == "0":
                    kept_rolls[i] = None
            

if __name__ == "__main__":
    main()