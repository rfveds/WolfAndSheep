import sqlite3
import threading


class Database:
    def __init__(self):
        """baza danych"""

        '''pozycja startowa wilka'''
        self.wolf_start = [
            'B2'
        ]

        '''pozycje startowe owiec'''
        self.sheep_start = [
            'B8',
            'D8',
            'F8',
            'H8',
        ]

        '''polaczenie z baza danych'''
        self.connection = sqlite3.connect('./game.db', check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.lock = threading.Lock()

    def setup_db(self):
        """tworzy baze danych"""

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Turn(
                                current_player INT, 
                                piece INT,
                                winner NULL,
                                  mode INT
                                )''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS Piece(
                                id INT,
                                position TEXT
                                )''')
        self.connection.commit()

    def select_whose_turn(self):
        """zwraca czyja jest tura"""

        try:
            self.lock.acquire(True)
            self.cursor.execute('''SELECT current_player FROM Turn''')
            player = self.cursor.fetchall()

            if len(player) == 0:
                return None
            else:
                return player[0][0]
        except:
            print('odswiez strone')
        finally:
            self.lock.release()

    def select_which_piece(self):
        """jaki pionek zaznaczony"""

        self.cursor.execute('''SELECT piece FROM Turn''')
        piece = self.cursor.fetchall()

        return piece[0][0]

    def select_pos(self, piece_id):
        """pobiera z bazy pozycje pionkow na planszy po id"""

        try:
            self.lock.acquire(True)
            self.cursor.execute('''SELECT position FROM Piece WHERE id = (?)''', str(piece_id))
            data = self.cursor.fetchall()
            position_str = data[0][0]
            row = int(position_str[1:]) - 1
            col = ['ABCDEFGH'[i] for i in range(8)].index(position_str[0])

        except:
            print('odswiez strone')
        finally:
            self.lock.release()

        return col, row

    def move(self, x, y, piece_id):
        """ustawia nowa pozucje w bazie danych pionka o danym id"""
        position = "{}{}".format('ABCDEFGH'[x], y + 1)
        self.cursor.execute('''UPDATE Piece SET position = (?) WHERE id = (?)''', (position, str(piece_id)))
        self.connection.commit()

    def seed_data(self):
        """ustawia poczatkowe dane planszy"""

        if not self.select_whose_turn():
            '''ustawienie pierwszego ruchu na wilka'''
            self.cursor.execute('''INSERT INTO Turn(current_player) VALUES(0)''')
            for wolf_position in self.wolf_start:
                self.cursor.execute('''INSERT INTO Piece(id, position) VALUES(?, ?)''', (4, wolf_position))
            i = 0
            for sheep_position in self.sheep_start:
                self.cursor.execute('''INSERT INTO Piece(id, position) VALUES(?, ?)''', (i, sheep_position))
                i += 1
        self.connection.commit()

    def reset_db(self):
        """czysci baze danych"""

        self.cursor.execute('''DELETE FROM Turn''')
        self.cursor.execute('''DELETE FROM Piece''')
        self.connection.commit()

    def next_turn(self, turn):
        """zmienia czyja tura"""
        try:
            self.lock.acquire(True)
            self.cursor.execute('''UPDATE Turn SET current_player = (?)''', str(turn))
            self.connection.commit()
        except:
            print('odswiez strone')
        finally:
            self.lock.release()

    def save_piece(self, piece):
        """zapisuje wybrany pionek"""
        self.cursor.execute('''UPDATE Turn SET piece = (?)''', str(piece))
        self.connection.commit()

    def wolf_won(self):
        self.cursor.execute('''UPDATE Turn SET winner = "wilk"''')
        self.connection.commit()

    def sheep_won(self):
        self.cursor.execute('''UPDATE Turn SET winner = "owce"''')
        self.connection.commit()

    def who_won(self):
        self.cursor.execute('''SELECT winner FROM Turn''')
        data = self.cursor.fetchall()

        return data

    def set_mode(self, mode):
        self.cursor.execute('''UPDATE Turn SET mode = (?)''', mode)
        self.connection.commit()

    def get_mode(self):
        try:
            self.lock.acquire(True)
            self.cursor.execute('''SELECT mode FROM Turn''')
            data = self.cursor.fetchall()

            return data[0][0]
        except:
            print('odswiez strone')
        finally:
            self.lock.release()
