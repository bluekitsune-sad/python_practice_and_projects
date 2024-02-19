# coding ✌(꘠益꘠)✌

# name = 'Saad yousuf'
# age = 20
#
# width, heigth = 10, 20
#
# your_name = input('Please enter your name:')
# print('Hi ' + your_name)
#
# num1 = input("Enter a number")
# num2 = input("Enter a number")
# # concatenation
# print(num1 + num2)
#
# number1 = int(input("Enter a number"))
# number2 = int(input("Enter a number"))
# print(number1 + number2)

# # tip app
# food_cost = float(input("Enter food cost: "))
# tip_percentage = float(input("Enter tip amount: ")) / 100
# tip_amount = food_cost * tip_percentage
# print(f'tip amount ${tip_amount}')
# total_food_amount = food_cost + tip_amount
# print("total $" + str(total_food_amount))

# #  weather app
# weather = 'rain'
# if weather == 'rain':
#     print('it is raining')
# elif weather == 'cloudy':
#     print('it si cloudy')
# elif weather == 'thunderStrom':
#     print('the S is capital')
# else:
#     print("its not raining")

# # score
# score = 59
# passing = False
# Superpassing = False
# if score >= 60 and score <= 100:
#     passing = True
# if 100 <= score <= 120:
#     Superpassing = True
# if ~passing | ~Superpassing:
#     print("Failed")

# # naming
# def say_my_name(greeting = "Assalamulaikum", name = "Saad Yousuf"):
#     return greeting + ", my name is " + name
#
#
# def conversation():
#     return '''
#     this
#     is
#     a
#     multi-Line
#     String
#     '''
#
#
# whats_my_name = say_my_name('Assalamulaikum', 'Saad')
# print(whats_my_name)
# print(conversation())

# # calulation
# def calculate(what_to_do, number1, number2):
#     if(what_to_do == "+"):
#         return number1 + number2
#     elif(what_to_do == "-"):
#         return number1 - number2
#     elif(what_to_do == "*"):
#         return number1 * number2
#     elif(what_to_do == "/"):
#         return number1 / number2
#     else:
#         return 0.97
#
# operator = "+"
# num1 = 2
# num2 = 6
# result = calculate(operator, num1, num2)
# if(result == 0.97):
#     print("An error has occured")
# else:
#     print(f'The operation of {operator} on {num1} and {num2} is {result}')

# # nested Food Calculation
# def calculate_Total(food, tip_percentage) -> float:
#     return food + calculater_tip(food, tip_percentage)
#
#
# def calculater_tip(food, tip_per) -> float:
#     return food * (tip_per / 100)
#
#
# def casher(food_price: float, tip_percentage: float) -> None:
#     print('\n\n\n')
#     print('--------------------------------')
#     print(f'🥘 Food Amount: ${food_price}')
#     print(f'⚖️ Tip Amount: ${tip_percentage}')
#     print('\n')
#     print(f'💰 Total Amount: ${calculate_Total(food_price, tip_percentage)}')
#     print('--------------------------------')
#     print('\n\n\n')
#
#
# casher(100, 20)

# big guy
# to import // from File.subFile import funcName
# def the_bigger_one(number1: float, number2: float) -> float:
#     if number1 > number2:
#         return number1
#     elif number1 < number2:
#         return number2
#     else:
#         return 0.91
#
#
# result = the_bigger_one(2, 3)
# if result == 0.91:
#     print("Either there is an error or you provided the same number two times")
# else:
#     print("the Bigger number is " + str(result))

# Lamda
# the_Trio_Sum = lambda a, b, c: a + b + c;
# assert the_Trio_Sum(1, 2, 3) == 6, 'the sum of 1+2+3 is 3 which is not the case'
#
# def licking_and_Tasting():
#     assert the_Trio_Sum(2, 4, 6) == 12, '❌ sum(2,4.6) does not return 12 like it should'
#
#     assert the_Trio_Sum(-20, 20, -20) == -20
#     assert the_Trio_Sum(20, 20, 20) == 60
#     assert the_Trio_Sum(560, 780, 911) == 2251
#
#     print('Sum Function: All Tests Passsed (4/4) ✅')
#
#
# licking_and_Tasting()

# Array
# fruit = ['apple','banana']

# LISTS (ARRAYS)
# methods list.append() vs. functions print()
#
# fruits = ['🍎', '🍐', '🍊', '🍌', '🍪', 2, 5, 'hi', 8.5, [4, 3]]
# print(fruits)
# fruits.append('🍊')
# print(fruits)
# fruits.append('🍓')
# print(fruits)

# Indexing
# print(fruits[0])
# print(fruits[1])
# print(fruits[2])
# print(fruits[-1])

# Slicing
# print(fruits[0:3]) # first inclusive, 2nd exclusive
# print(fruits[0:4])
# print(fruits[0: len(fruits) - 1])
# print('Hi my name is Sad!'[-1])
# print(fruits[::-1]) # reverse the list
# print(fruits[0:5:2]) # [from : to : StepBy]
# print(fruits[::-1]) # This will reverse the array

# # Dictionary
# person = {
#     'name': 'SAAD YOUSUF',
#     'age': '20',
#     'clothing': 'hoddie & pants',
#     'joke': 'What kind of cars do eggs drive? Yolkswagens.',
#     'electronic': 'Computer',
# }
# print(person['joke'])
# print(list(person.value()))
# print(person.value())
# print(person.key())

# # introductory information
# def introducer(what_i_want: str) -> str:
#     introduction = {
#         'name': 'SAAD YOUSUF',
#         'age': '20',
#         'clothing': 'hoddie & pants',
#         'joke': 'What kind of cars do eggs drive? Yolkswagens.',
#         'electronic': 'Desktop Computer',
#         'assets': 0.69,
#         'debt': 690,
#         'netWorth': lambda: introduction['assets'] - introduction['debt'],
#         'phoneNumber': '001-7-3-3-14'
#     }
#     return introduction[what_i_want]
#
#
# print(
#     f"\n\nAssaalamualikum, my name is {introducer('name')}, \nI am wearing a {introducer('clothing')}, \nThe device "
#     f"I am using to code is {introducer('electronic')}, \nmy number is {introducer('phoneNumber')}, \nmy networth is {introducer('netWorth')()}")
# # something interesting that i have called a function from a function {introducer('netWorth')()}

# # Tuples
# # this is immutable
# tuplee = (1, 2)
# print(tuplee)

# # Sets
# popular_programming_language = ['Java', 'Python', 'JavaScript']
# unpopular_programming_language = ['Ruby', 'Python', 'Bash', 'CSS']
#
# total_programming_language = popular_programming_language + unpopular_programming_language
# # set(total_programming_language)
#
# print(total_programming_language)
# print(set(total_programming_language))
# print('Java' in set(total_programming_language))

# # converter
# def unique(convert_this): return list(set(convert_this))
#
# uniquewe = lambda convert_this_list: list(set(convert_this_list))
#
# print(unique(['ruby', 'ruby', 'python', 'ruby', 'python', 'ruby', 'SQL', 'JAVA', 'javascript']))
# print(uniquewe(['ruby', 'ruby', 'python', 'ruby', 'python', 'ruby', 'SQL', 'JAVA', 'javascript']))

# # Loops
# food = ['🥨', '🌭', '🍔', '🍕', '🥟']
# print('food:', food[0], 0)
# print('food:', food[1], 1)
# print('food:', food[2], 2)
# print('food:', food[3], 3)
# print('food:', food[4], 4)
# for foods in food:
#     print(foods)

# for index, foods in enumerate(food):
#     print('food:', foods, index)
# enumerate() returns everything with indexes and make them tuples

# Run 5 Times
# for _ in range(5):
#     print("haha")

# append 10 spaghetti
# for _ in range(10):
#     food.append('🍝')

# print(food)

# # unPacking Tuples
# things = ('0', '(╯°□°）╯︵ ┻━┻')
# print(things)
# index, emote = ('0', '(╯°□°）╯︵ ┻━┻')
# print(index, '\n', emote)

# # while Loops
# qazi = 'sitting'
# while qazi != 'standing':
#     print('Get Your Fat Butt Up 💯!')

# counter = 0
# while counter < 10:
#     print(counter)
#     counter += 1

# Doubling the numbers

"""
double([1, 2, 3, 4, 5])
[2, 4, 6, 8, 10]
"""

# def double(numbers: list) -> list:
#     result = []
#     for number in numbers:
#         result.append(number * 2)
#
#     return result

# print(double([1, 2, 3]))

# create empty list
# loop through & append to that list
# return that list

# # My version of double
# def double_my_version(numbers: list) -> list:
#     i = 0
#     for i in range(len(numbers)):
#         numbers[i] = numbers[i] + numbers[i]
#         i += 1
#
#     return numbers


# print(double_my_version([1, 2, 3, 4, 5, 6, 7]))

# # counting Words in string
# def start_counting(strung, split_by=' '):
#     return strung.split(split_by)


# print(start_counting("b now b vw b ji"))
# print(start_counting("b now b vw b ji", 'vw'))

# # Sum of the list
# def sum_of_list(data):
#     sum = 0
#     for number in data:
#         sum += number
#     return sum

# def same_but_complex(data):
#     data.append(0)
#     for number in data[0:-1]:
#         data[len(data)-1] += number
#     return data[-1]

# print(sum_of_list([1, 2, 3, 4, 5, 6, 7]))
# print(same_but_complex([1, 2, 3, 4, 5, 6, 7]))

# # finding the max
# def findMax(dataStream):
#     dataStream.sort()
#     dataStream.reverse()
#     return dataStream[0]
#
#
# def find_max(numbers):
#     current_max = numbers[0]
#     for number in numbers:
#         if number > current_max:
#             current_max = number
#
#     return current_max


# print(find_max([1, 2, 3, 10, 17, 4, 5, 6]))

# findMaxx = lambda dataStream: sorted(dataStream, reverse=True)[0]

# print(findMax([4, 5, 6, 4, 2, 3, 1]))
# print(findMaxx([-4, -5, -6, -4, -2, -3, -1]))

# # Dictionary Practice
# '''
# >>> word_frequency('I love Batman because I am Batman')
# {'I': 2, 'love': 1, 'Batman': 2, 'because': 1, 'am': 1}
# '''


# def word_frequency(phrase):
#     result = {}
#     words = phrase.split()
#     for word in words:
#         if word not in result:
#             result[word] = 1
#         else:
#             result[word] += 1
#
#     return result

# print(word_frequency('I love Batman because I am Batman'))

# print(word_frequency(input('please enter your phrase: ')))

# result = {
#   'I': 2,
#   'love': 1,
#   'Batman': 2,
#   'because': 1,
#   'am': 1,
# }

# # loop 1
# is 'I' in result? no
# set the key to 'I' and value to 1

# # loop 2
# is 'love' in result? no
# set the key to 'love' and value to 1

# # loop 3
# is 'Batman' in result? no
# set the key to 'Batman' and value to 1

# # loop 4
# is 'because' in result? no
# set the key to 'because' and value to 1

# # loop 5
# is 'I' in result? yes
# increment the value of 'I' key by 1

# # loop 6
# is 'am' in result? no
# set the key to 'am' and value to 1

# # loop 7
# is 'Batman' in result? yes
# increment the value of 'Batman' key by 1

# # Higher Order Functions
# map
# filter

# data.map((e)->{e=e*2})  JAVASCRIPT
# data = [1, 2, 3, 4, 5, 6, 7]
# print(list(map(lambda num: num ** 2, data))) # map(function,data)

# print(list(filter(lambda num: num % 2 == 0, data)))  # This Checks

# # List Comprehensions
# data = [1, 2, 3, 4, 5, 6, 7]

# for Odd only using list comprehension instead of filter
# print([datas for datas in data if datas % 3 == 0])
# print([datas ** 7 for datas in data if datas % 2 != 0])

# map replacement with list comprehension
# print([datas ** 2 for datas in data])

# # SPECIAL BUILT-IN FUNCTIONS with Python
# >>> sum([1, 2, 3])
# 6
# >>> len([1, 2, 3])
# 3
# >>> max([1, 2, 3])
# 3
# >>> max([1, 2, 3, 10, 5, 7])
# 10

# >>> min([1, 50, -7, 337])
# -7

# def the_Trio_Sum():
