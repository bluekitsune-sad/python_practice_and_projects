# Medium level projects

# # Password Generator
# from cryptrography.fernet import Fernet
#
#
# def write_key():
#     key = Fernet.generate_key()
#     with open('key.key', 'wb') as key_file:
#         key_file.write(key)
#
#
# def load_key():
#     file = open("key.key", "rb")
#     key = file.read()
#     file.close()
#     return key
#
#
# def view():
#     name = input('Account Name: ')
#     pwd = input('Password: ')
#
#     with open('passwords.txt', 'r') as f:
#         for line in f.readlines():
#             print(line.rstrip())  # rstrip will strip the special character "\n"
#             data = line.rstrip()
#             user, password = data.split("|")
#             print("User: " + user + " Password: " + fer.decrypt(password.encode()).decode())
#
#
# def add():
#     name = input('Account Name: ')
#     pwd = input('Password: ')
#
#     with open('passwords.txt', 'a') as f:  # with keyword will close the file automatically after use a = append
#         # f.write(name + "|" + pwd + "\n")
#         f.write(name + "|" + fer.encrypt(pwd.encode()).decode() + "\n")
#
#
# Masterpwd = input("What is the master password: ")
# key = load_key() + Masterpwd.encode()
# fer = Fernet(key)
#
#
# mode = input("Would you like to add new password(add) or to view existing one(view): ")
#
# while True:
#     if mode == 'q':
#         break
#
#     if mode == "view":
#         view()
#
#     elif mode == "add":
#         add()
#
#     else:
#         print("enter a valid option")

# # multiplayer dice game
# import random
#
#
# def roll():
#     min_value = 1
#     max_value = 6
#     roll = random.randint(min_value, max_value)
#
#     return roll
#
#
# while True:
#     players = input("Enter the number of players (2 - 4): ")
#     if players.isdigit():
#         players = int(players)
#         if 2 <= players <= 4:
#             break
#         else:
#             print("Must be between 2 - 4 players.")
#     else:
#         print("Invalid, try again.")
#
# max_score = 50
# player_scores = [0 for _ in range(players)]
#
# while max(player_scores) < max_score:
#     for player_idx in range(players):
#         print("\nPlayer number", player_idx + 1, "turn has just started!")
#         print("Your total score is:", player_scores[player_idx], "\n")
#         current_score = 0
#
#         while True:
#             should_roll = input("Would you like to roll (y)? ")
#             if should_roll.lower() != "y":
#                 break
#
#             value = roll()
#             if value == 1:
#                 print("You rolled a 1! Turn done!")
#                 current_score = 0
#                 break
#             else:
#                 current_score += value
#                 print("You rolled a:", value)
#
#             print("Your score is:", current_score)
#
#         player_scores[player_idx] += current_score
#         print("Your total score is:", player_scores[player_idx])
#
# max_score = max(player_scores)
# winning_idx = player_scores.index(max_score)
# print("Player number", winning_idx + 1, "is the winner with a score of:", max_score)

# # Madlibs Generator
#
# with open("story.txt", "r") as f:
#     story = f.read()
#
# words = set()
# start_of_word = -1
#
# target_start = "<"
# target_end = ">"
#
# for i, char in enumerate(story):
#     if char == target_start:
#         start_of_word = i
#
#     if char == target_end and start_of_word != -1:
#         word = story[start_of_word: i + 1]  # Slicing
#         words.add(word)
#         start_of_word = -1
#
# answers = {}
#
# for word in words:
#     answer = input("Enter a word for " + word + ": ")
#     answers[word] = answer
#
# for word in words:
#     story = story.replace(word, answers[word])
#
# with open("ChangedStory.txt","w") as f:
#     f.write(story)
#
# print(story)

# # Timed Math Challenge
#
# import random
# import time
#
# OPERATORS = ["+", "-", "*"]
# MIN_OPERAND = 3
# MAX_OPERAND = 12
# TOTAL_PROBLEMS = 10
#
#
# def generate_problem():
#     left = random.randint(MIN_OPERAND, MAX_OPERAND)
#     right = random.randint(MIN_OPERAND, MAX_OPERAND)
#     operator = random.choice(OPERATORS)
#
#     expr = str(left) + " " + operator + " " + str(right)
#     answer = eval(expr)  # eval provides solution to mathematical explorations
#     return expr, answer
#
#
# wrong = 0
# input("Press enter to start!")
# print("----------------------")
#
# start_time = time.time()
#
# for i in range(TOTAL_PROBLEMS):
#     expr, answer = generate_problem()
#     while True:
#         guess = input("Problem #" + str(i + 1) + ": " + expr + " = ")
#         if guess == str(answer):
#             break
#         wrong += 1
#
# end_time = time.time()
# total_time = round(end_time - start_time, 2)
#
# print("----------------------")
# print("Nice work! You finished in", total_time, "seconds!")

# # Slot Machine
#
# import random
#
# MAX_LINES = 3
# MAX_BET = 100
# MIN_BET = 1
#
# ROWS = 3
# COLS = 3
#
# symbol_count = {
#     "A": 2,
#     "B": 4,
#     "C": 6,
#     "D": 8
# }
#
# symbol_value = {
#     "A": 5,
#     "B": 4,
#     "C": 3,
#     "D": 2
# }
#
#
# def check_winnings(columns, lines, bet, values):
#     winnings = 0
#     winning_lines = []
#     for line in range(lines):
#         symbol = columns[0][line]
#         for column in columns:
#             symbol_to_check = column[line]
#             if symbol != symbol_to_check:
#                 break
#         else:
#             winnings += values[symbol] * bet
#             winning_lines.append(line + 1)
#
#     return winnings, winning_lines
#
#
# def get_slot_machine_spin(rows, cols, symbols):
#     all_symbols = []
#     for symbol, symbol_count in symbols.items():
#         for _ in range(symbol_count):
#             all_symbols.append(symbol)
#
#     columns = []
#     for _ in range(cols):
#         column = []
#         current_symbols = all_symbols[:]  # copy the all_symbols to current_symbols
#         for _ in range(rows):
#             value = random.choice(current_symbols)
#             current_symbols.remove(value)
#             column.append(value)
#
#         columns.append(column)
#
#     return columns
#
#
# def print_slot_machine(columns):
#     for row in range(len(columns[0])):
#         for i, column in enumerate(columns):
#             if i != len(columns) - 1:
#                 print(column[row], end=" | ")
#             else:
#                 print(column[row], end="")
#
#         print()
#
#
# def deposit():
#     while True:
#         amount = input("What would you like to deposit? $")
#         if amount.isdigit():
#             amount = int(amount)
#             if amount > 0:
#                 break
#             else:
#                 print("Amount must be greater than 0.")
#         else:
#             print("Please enter a number.")
#
#     return amount
#
#
# def get_number_of_lines():
#     while True:
#         lines = input(
#             "Enter the number of lines to bet on (1-" + str(MAX_LINES) + ")? ")
#         if lines.isdigit():
#             lines = int(lines)
#             if 1 <= lines <= MAX_LINES:
#                 break
#             else:
#                 print("Enter a valid number of lines.")
#         else:
#             print("Please enter a number.")
#
#     return lines
#
#
# def get_bet():
#     while True:
#         amount = input("What would you like to bet on each line? $")
#         if amount.isdigit():
#             amount = int(amount)
#             if MIN_BET <= amount <= MAX_BET:
#                 break
#             else:
#                 print(f"Amount must be between ${MIN_BET} - ${MAX_BET}.")
#         else:
#             print("Please enter a number.")
#
#     return amount
#
#
# def spin(balance):
#     lines = get_number_of_lines()
#     while True:
#         bet = get_bet()
#         total_bet = bet * lines
#
#         if total_bet > balance:
#             print(
#                 f"You do not have enough to bet that amount, your current balance is: ${balance}")
#         else:
#             break
#
#     print(
#         f"You are betting ${bet} on {lines} lines. Total bet is equal to: ${total_bet}")
#
#     slots = get_slot_machine_spin(ROWS, COLS, symbol_count)
#     print_slot_machine(slots)
#     winnings, winning_lines = check_winnings(slots, lines, bet, symbol_value)
#     print(f"You won ${winnings}.")
#     print(f"You won on lines:", *winning_lines)
#     return winnings - total_bet
#
#
# def main():
#     balance = deposit()
#     while True:
#         print(f"Current balance is ${balance}")
#         answer = input("Press enter to play (q to quit).")
#         if answer == "q":
#             break
#         balance += spin(balance)
#
#     print(f"You left with ${balance}")
#
#
# main()

# # Turtle Racing
#
# import turtle
# import time
# import random
#
# WIDTH, HEIGHT = 700, 600
# COLORS = ['red', 'green', 'blue', 'orange', 'yellow', 'black', 'purple', 'pink', 'brown', 'cyan']
#
#
# def get_number_of_racers():
#     racers = 0
#     while True:
#         racers = input('Enter the number of racers (2 - 10): ')
#         if racers.isdigit():
#             racers = int(racers)
#         else:
#             print('Input is not numeric... Try Again!')
#             continue
#
#         if 2 <= racers <= 10:
#             return racers
#         else:
#             print('Number not in range 2-10. Try Again!')
#
#
# def race(colors):
#     turtles = create_turtles(colors)
#
#     while True:
#         for racer in turtles:
#             distance = random.randrange(1, 20)
#             racer.forward(distance)
#
#             x, y = racer.pos()
#             if y >= HEIGHT // 2 - 10:
#                 return colors[turtles.index(racer)]
#
#
# def create_turtles(colors):
#     turtles = []
#     spacingx = WIDTH // (len(colors) + 1)
#     for i, color in enumerate(colors):
#         racer = turtle.Turtle()
#         racer.color(color)
#         racer.shape('turtle')
#         racer.left(90)
#         racer.penup()  # start drawing
#         racer.setpos(-WIDTH // 2 + (i + 1) * spacingx, -HEIGHT // 2 + 20)
#         racer.pendown()  # stop drawing
#         turtles.append(racer)
#
#     return turtles
#
#
# def init_turtle():
#     screen = turtle.Screen()
#     screen.setup(WIDTH, HEIGHT)
#     screen.title('Turtle Racing!')
#
#
# racers = get_number_of_racers()
# init_turtle()
#
# random.shuffle(COLORS)  # mix the color list
# colors = COLORS[:racers]
#
# winner = race(colors)
# print("The winner is the turtle with color:", winner)
# time.sleep(5)

# Typing test

import curses  # for styling
from curses import wrapper
import time
import random


def start_screen(stdscr):
    stdscr.clear()
    stdscr.addstr("Welcome to the Speed Typing Test!")
    stdscr.addstr("\nPress any key to begin!")
    stdscr.refresh()
    stdscr.getkey()


def display_text(stdscr, target, current, wpm=0):
    stdscr.addstr(target)
    stdscr.addstr(1, 0, f"WPM: {wpm}")

    for i, char in enumerate(current):
        correct_char = target[i]
        color = curses.color_pair(1)
        if char != correct_char:
            color = curses.color_pair(2)

        stdscr.addstr(0, i, char, color)


def load_text():
    with open("text.txt", "r") as f:
        lines = f.readlines()
        return random.choice(lines).strip()


def wpm_test(stdscr):
    target_text = load_text()
    current_text = []
    wpm = 0
    start_time = time.time()
    stdscr.nodelay(True)

    while True:
        time_elapsed = max(time.time() - start_time, 1)
        wpm = round((len(current_text) / (time_elapsed / 60)) / 5)

        stdscr.clear()
        display_text(stdscr, target_text, current_text, wpm)
        stdscr.refresh()

        if "".join(current_text) == target_text:
            stdscr.nodelay(False)
            break

        try:
            key = stdscr.getkey()
        except:
            continue

        if ord(key) == 27:
            break

        if key in ("KEY_BACKSPACE", '\b', "\x7f"):
            if len(current_text) > 0:
                current_text.pop()
        elif len(current_text) < len(target_text):
            current_text.append(key)


def main(stdscr):
    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_WHITE, curses.COLOR_BLACK)

    start_screen(stdscr)
    while True:
        wpm_test(stdscr)
        stdscr.addstr(2, 0, "You completed the text! Press any key to continue...")
        key = stdscr.getkey()

        if ord(key) == 27:
            break


wrapper(main)
# run this through terminal also pip install windows-curses
