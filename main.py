import argparse
import os
import json
import random
from table import Table


YAHTZEE_CHOICES_PATH = "choices.json"
TEST_ROLL_BOOL = False
TEST_ROLLS = []

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

def roll(kept_rolls): # add boolean that if TEST_ROLL_BOOL is true, you can add your own rolls instead of random rolls
    if TEST_ROLL_BOOL:
        return [1, 1, 1, 1, 1]
    for i in range(len(kept_rolls)):
        if kept_rolls[i] is None:
            kept_rolls[i] = random.randint(1, 6)
    return kept_rolls

def scoresheet_choice(options, table: Table, rolls):
    if options is not None:
        print(f"Your scoresheet choice must be one of these options: {options}")
    selection = input("What scoresheet choice do you want to use for this turn? (ex: select '7' or '3_of_a_kind' to choose '3 of a kind'): ")
    validity = table.check_selection(selection)
    while validity == "invalid" or validity == "taken" or (options is not None and table.table[validity][0] not in options):
        if validity == "invalid":
            selection = input("That was an invalid input, please enter a valid input (ex: select '7' or '3_of_a_kind' to choose '3 of a kind'): ")
            validity = table.check_selection(selection)
        elif validity == "taken":
            selection = input(f"{selection} was already taken, please enter one of these options, {options}: ")
            validity = table.check_selection(selection)
        else:
            selection = input(f"That is not one of the options, please enter one of these options, {options}: ")
            validity = table.check_selection(selection)
    table.add_selection(selection, rolls)
    

def main():
    print("Welcome to Yahtzee")
    print("After each roll, you will be provided with the current turn and roll.")
    print("If you ever need help or instructions on the application, write 'help'.")
    print("If you ever need rules for Yahtzee, you can visit this site: https://winning-moves.com/images/YAHTZEERULES_2022.pdf or write 'rules'.")
    #print("If you want to display the current table, write 'table'")
    #display_table()
    table = Table()
    #table.calculate_score()
    for turn in range(1, 14):
        table.display()
        kept_rolls = [None] * 5
        for roll_num in range(1, 4):
            print(f"turn: {turn}")
            print(f"roll: {roll_num}")
            rolls = roll(kept_rolls)
            print(f"Your die results are: {rolls}")
            if roll_num < 3:
                keep_choice = input("Which numbers do you want to keep? (ex: format is '01001' if you want to keep the second and fifth die): ")
                while keep_choice != "" and len(keep_choice) != 5: #may need to add checks for specifically 0s and 1s
                    keep_choice = input("That is not the correct format, the format should be made up of 0s and 1s and be 5 characters long (ex: format is '01001' if you want to keep the second and fifth die): ")
                if keep_choice == "":
                    kept_rolls = [None] * 5
                else:
                    for i in range(len(keep_choice)):
                        if keep_choice[i] == "0":
                            kept_rolls[i] = None
                
        if len(set(kept_rolls)) == 1 and table.table[11][1]:
            print("You scored another Yahtzee!")
            if table.table[rolls[0] - 1][1] is None:
                #selection = rolls[0] - 1
                #print(f"Your joker selection was {table.table[rolls[0] - 1][0]}")
                options = table.table[rolls[0] - 1][0]
                scoresheet_choice(options, table, rolls)
            elif table.table[6][1] is None or table.table[7][1] is None or table.table[8][1] is None:
                options = []
                for i in range(6, 9):
                    if table.table[i][1] is None:
                        options.append(table.table[i][0])
                scoresheet_choice(options, table, rolls)
            else:
                options = []
                for i in range(9, 13):
                    if table.table[i][1] is None and i != 11: # skipping yahtzee
                        options.append(table.table[i][0])
                if not options:
                    for i in range(1, 7):
                        if table.table[i][1] is None:
                            options.append(table.table[i][0])
                scoresheet_choice(options, table, rolls)
        else:
            scoresheet_choice(None, table, rolls)
                #selection = input("What scoresheet choice do you want to use for this turn? (ex: select '7' or '3_of_a_kind' to choose '3 of a kind'): ")
                #while not table.add_selection(selection, kept_rolls):
                #    selection = input("That was an invalid input, please enter a valid input (ex: select '7' or '3_of_a_kind' to choose '3 of a kind'): ")
    print("You have finished your turns, here is your final scoresheet:")
    table.display()
    final_score, true_final_score = table.calculate_scores()
    print(f"\nYour final score was {final_score}")
    print(f"Your true score (without including 100 bonus per extra yahtzee) was {true_final_score}")

if __name__ == "__main__":
    main()