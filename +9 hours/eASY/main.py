# EASY level projects

# # QUiZ
#
# print('!! Welcome to Quiz Game !!')
#
# player_name = input("What do you want be referred to as: ")
# playing = input("Do you want to play a game kid: ")
#
# if playing.lower() != "yes":
#     quit()
#
# while playing == "yes":
#     print("Okay lets began")
#
#     questions = [
#         "What is the capital of France?\nA) Madrid\nB) Paris\nC) London\nD) Berlin",
#         "Which planet is known as the Red Planet?\nA) Earth\nB) Mars\nC) Jupiter\nD) Venus",
#         "What is the largest mammal in the world?\nA) Elephant\nB) Blue Whale\nC) Giraffe\nD) Rhino",
#         "Who wrote 'Romeo and Juliet'?\nA) Charles Dickens\nB) William Shakespeare\nC) Jane Austen\nD) Mark Twain",
#         "What is the boiling point of water?\nA) 90°C\nB) 100°C\nC) 120°C\nD) 80°C"
#     ]
#
#     answers = ['B', 'B', 'B', 'B', 'B']  # The correct answers
#     score = 0
#
#     for i in range(len(questions)):
#         print(questions[i])  # Display the question
#         user_answer = input("Enter your answer (A/B/C/D): ").strip().upper()  # Get the user's answer
#         if user_answer == answers[i]:
#             print("\nCorrect!")
#             score += 1
#         else:
#             print("Wrong!")
#         print()  # Print a newline for spacing
#
#     print(f"{player_name} has scored total of {score} out of {len(questions)}.")
#
#     playing = input("\nDo you want to play a game again: ")

# # Guessing Number
# import random
#
# rangeTOP = input("type a top range: ")
#
# if rangeTOP.isdigit():  # check if the string has a number instead of any string
#     rangeTOP = int(rangeTOP)
#     if rangeTOP <= 0:
#         print("Enter a number greater than 0")
# else:
#     print("Enter a number Next Time")
#     quit()
#
# generatedNum = random.randrange(-1, rangeTOP)  # 0 to 9
#
# gasCount = 0 # =3
#
# while True:
#     user_Guess = input("Make a guess: ")
#     if user_Guess.isdigit():  # check if the string has a number instead of any string
#         user_Guess = int(user_Guess)
#         if user_Guess <= 0:
#             print("\nEnter a number greater than 0")
#     else:
#         print("\nEnter a number Next Time")
#         continue  # will go to the top of the loop
#
#     if user_Guess == generatedNum:
#         print("You have Guessed correctly")
#         print(f"\nit took you {gasCount} to guess correct answer")
#         break
#     elif user_Guess <= generatedNum:
#         print("\nyou have guessed lower")
#         gasCount += 1
#     else:  # user_Guess >= generatedNum
#         print("\nyou have guessed higher")
#         gasCount += 1

# # ROCK PAPER SCISSOR
# import random
#
# user_win = 0
# AI_win = 0
#
# print("type number for corresponding option rock: 0, paper: 1, scissors: 2 and q to quit")
#
# options = ["rock", "paper", "scissors"]
#
# while True:
#     user_input = input("type your choice: ").upper()
#     if user_input == 'q':
#         break
#     if 0 >= user_input >= 2:  # the user input is not between 0 to 2
#         continue
#
#     random_number = random.randint(0, 2)
#     # rock: 0, paper: 1, scissors: 2
#     computer_pick = random_number
#     # computer_pick = options[random_number]
#     print(f"Computer has selected {computer_pick}.")
#
#     if user_input == 0 and computer_pick == 2:
#         print("the user has won the round")
#         user_win += 1
#         continue
#     elif user_input == 1 and computer_pick == 0:
#         print("the user has won the round")
#         user_win += 1
#         continue
#     elif user_input == 2 and computer_pick == 1:
#         print("the user has won the round")
#         user_win += 1
#         continue
#     else:
#         print("THE AI has won the round")
#         AI_win += 1
#
# print(f"you have won {user_win} times and the AI won {AI_win} times")
# print("GoodBye")

# Choice your own adventure
from PIL import Image

name = input("Type your name: ")
print("Welcome", name, "to this adventure!")

died = False

answer = input(
    "You are on a dirt road, it has come to an end and you can go left or right. Which way would you like to go? ").lower()

if answer == "left":
    answer = input(
        "You come to a river, you can walk around it or swim accross? Type walk to walk around and swim to swim across: ")

    if answer == "swim":
        print("You swam across and were eaten by an alligator.")
    elif answer == "walk":
        print("You walked for many miles, ran out of water and YOU DIED.")
        died = True
    else:
        print('Not a valid option. YOU DIED..')
        died = True

elif answer == "right":
    answer = input(
        "You come to a bridge, it looks wobbly, do you want to cross it or head back (cross/back)? ")

    if answer == "back":
        print("You go back and DIED..")
        died = True
    elif answer == "cross":
        answer = input(
            "You cross the bridge and meet a stranger. Do you talk to them (yes/no)? ")

        if answer == "yes":
            print("You talk to the stanger and they give you gold. You WIN!")
        elif answer == "no":
            print("You ignore the stranger and they are offended and YOU DIED.")
            died = True
        else:
            print('Not a valid option. YOU DIED.')
            died = True
    else:
        print('Not a valid option. YOU DIED.')
        died = True

else:
    print('Not a valid option. YOU DIED.')
    died = True

if died == True:
    im = Image.open('./gmaeover.gif')
print("Thank you for trying", name)
