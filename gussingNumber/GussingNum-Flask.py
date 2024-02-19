from flask import Flask, render_template, request
from random import choice

app = Flask(__name__)

databasse = {}

if 'guesses' not in databasse:
    databasse['guesses'] = []

if 'computer_number' not in databasse:
    databasse['computer_number'] = choice(range(1, 101))


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        guess = request.form['number_guess']
        guessed_number = int(guess)
        databasse['guesses'].append(check_number_show_message(guessed_number, databasse['computer_number']))

    return render_template('index.html', guesses=reversed(databasse['guesses']))


def check_number_show_message(guessed_number, computer_number):
    if guessed_number < computer_number:
        return f'{guessed_number} is too low'

    elif guessed_number > computer_number:
        return f'{guessed_number} is too high'

    else:

        return f'{guessed_number} is correct'


@app.route('/reset', methods=['GET', 'POST'])
def reset():
    databasse['guesses'] = []
    databasse['computer_number'] = choice(range(1, 101))
    return render_template('index.html', guesses=reversed(databasse['guesses']))


app.run(host='0.0.0.0', port=81)
