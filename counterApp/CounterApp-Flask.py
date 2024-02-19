from flask import Flask

app = Flask(__name__)

magicaldb = {'number': 0}

home_page = lambda number: f'''
    <link rel="stylesheet" href="./static/style.css">

    <span>{number}</span>
    <div>
    <form action="/decrement" method="POST">
      <button id='decrement' type="submit">-</button>
    </form>
    <form action="/increment" method="POST">
      <button id='increment' type="submit">+</button>
    </form>
    </div>
    '''


@app.route('/')
def homePage():
    return home_page(magicaldb['number'])


@app.route('/increment', methods=['POST'])
def increment():
    magicaldb['number'] += 1
    return home_page(magicaldb["number"])


@app.route('/decrement', methods=['POST'])
def decrement():
    magicaldb['number'] -= 1
    return home_page(magicaldb["number"])


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=81)
