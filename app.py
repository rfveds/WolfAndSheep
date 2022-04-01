from flask import Flask, render_template, redirect, request, session, make_response, url_for
from db import Database
from board import Board

app = Flask(__name__)

database = Database()
database.setup_db()
database.seed_data()

app.secret_key = 'UXH7*^w^c^()_+'


@app.route('/move_id/<int:id>')
def move_id(id):
    piece = id
    database.save_piece(piece)
    return redirect('/board')


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.args.get('mode'):
        mode = request.args.get('mode')
        database.set_mode(mode)
        if mode == '3':
            return redirect('/player')
        return redirect('/board')
    return render_template('form.html')


@app.route('/player', methods=['GET', 'POST'])
def player():
    if request.method == 'POST':
        res = make_response('')
        res.set_cookie('player', request.form.get('player'))
        res.headers['location'] = url_for('show_board')
        return res, 302

    return render_template('player.html')


@app.route('/reset', )
def reset():
    database.reset_db()
    database.setup_db()
    database.seed_data()
    resp = make_response('')
    resp.set_cookie('player', '', expires=0)
    return redirect('/form')


@app.route('/win')
def win():
    winner = database.who_won()
    return render_template('win.html', winner=winner)


@app.route('/board', methods=['POST', 'GET'])
def show_board():
    turn = int(database.select_whose_turn())
    board = Board(database)
    mode = database.get_mode()

    # gra z wilkiem
    if mode == 1 and turn == 0:
        board.wolf_ai()

    # gra z owcami
    if mode == 2 and turn == 1:
        board.sheep_ai()

    # ai vs ai
    if mode == 5:
        if turn == 0:
            board.wolf_ai()
        else:
            board.sheep_ai()

    board = Board(database)

    if board.check_win() is not None:
        return redirect('/win')

    return render_template('board.html', board=board.board, turn=database.select_whose_turn(), mode=str(mode)
                           )


@app.route('/move/<int:x>/<int:y>')
def move(x, y):
    board = Board(database)
    piece = database.select_which_piece()
    turn = int(database.select_whose_turn())
    mode = database.get_mode()
    p = -1

    if board.check_win() is not None:
        return redirect('/win')

    if request.cookies.get('player'):
        p = int(request.cookies.get('player'))

    if mode == 1 and turn == 1 and piece in range(0, 4):
        board.move_player(x, y, piece)

    if mode == 2 and turn == 0 and piece == 4:
        board.move_player(x, y, piece)

    if mode == 3:
        if p == turn:
            board.move_player(x, y, piece)

    if mode == 4:
        if turn == 0 and piece == 4:
            board.move_player(x, y, piece)
        if turn == 1 and piece in range(0, 4):
            board.move_player(x, y, piece)

    return redirect('/board')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5120', debug=True)
