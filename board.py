import copy, random
import shutil


class Board:
    def __init__(self, database):

        self.database = database
        self.board_spaces = []

        # | . | x | . |
        # | x | o | x |
        # | . | x | . |

        self.directions = [(1, 1), (-1, 1), (1, -1), (-1, -1)]

        for i in range(0, 8):
            row = []
            for j in range(0, 8):
                row.append(' ')
            self.board_spaces.append(row)

        self.sheep = []
        for i in range(4):
            self.sheep.append(database.select_pos(i))

        self.wolf = database.select_pos(4)

        self.board = copy.deepcopy(self.board_spaces)
        for i in range(len(self.sheep)):
            self.board[self.sheep[i][1]][self.sheep[i][0]] = str(i)
        self.board[self.wolf[1]][self.wolf[0]] = '4'

    def wolf_ai(self):

        moves = self.get_possible_moves(4)

        # jesli owca moze zablokowac wilka, wilk ucieka
        if len(self.sheep_block_wolf()) > 0:
            print("####")
            print(self.wolf_no_block())
            moves = self.wolf_no_block()
            chosen_move = self.highest_move(moves)
            if len(chosen_move) == 0:
                chosen_move = self.highest_move(self.get_possible_moves(4))
        else:
            print('!!!!!')
            chosen_move = self.highest_move(moves)

        # wolf_random_moves = []
        # for m in self.get_possible_moves(4):
        #     wolf_random_moves.append(m)
        # chosen_move = random.choice(wolf_random_moves)

        if len(chosen_move) != 0:
            print(chosen_move)
            self.move_player(chosen_move[0], chosen_move[1], 4)

    def sheep_ai(self):

        # ruchy tych ktore sa najnizej
        moves = self.sheep_lowest()
        print(moves)
        # jesli wiecej niz jeden
        if len(moves) > 1:
            print(moves)
            print('wiecej niz jeden ruch dla tych najnizej')

            # usun tych ktore sa blisko wilka
            if len(self.remove_close_to_wolf(moves)) > 1:
                print('wiecej niz jedna ktora nie jest blisko wilka')
                moves = self.remove_close_to_wolf(moves)
                print(moves)

                # ta ktora ma jeden ruch
                if len(self.sheep_with_one_move(moves)) == 1:
                    print('jest taka ktora ma jeden ruch')
                    moves = self.sheep_with_one_move(moves)
                    moves = moves[0]
                # wiecej niz jedne ruch
                elif len(self.sheep_with_one_move(moves)) > 1:
                    print('wiecej niz jedna z jednym ruchem')
                    moves = moves[0]
                # nie ma takiej z jednym ruchem na dole
                else:
                    print('nie ma takiej ktora ma jeden ruch')
                    moves = self.closest_to_wolf(moves)

            elif len(self.remove_close_to_wolf(moves)) == 1:
                print('jedna ktora nie jest blisko wilka')
                moves = self.remove_close_to_wolf(moves)
                print(moves)
                moves = moves[0]

            else:
                print('nie ma takich ktore nie sa blisko wilka')
                # wszystkie dostepne
                moves = self.sheep_moves()
                # nie te ktore sa blisko wilka
                moves = self.remove_close_to_wolf(moves)
                if len(moves) > 0:
                    print(moves)
                    moves = moves[0]

        elif len(moves) == 1:
            print('jedna owca na dole')
            if len(self.remove_close_to_wolf(moves)) >= 1:
                print('da sie')
                print(moves)
                moves = self.remove_close_to_wolf(moves)
                moves = moves[0]
            elif len(self.remove_close_to_wolf(moves)) == 0:
                print('nie mozna bo blokuje wilka')
                moves = self.sheep_moves()
                # nie te ktore sa blisko wilka
                moves = self.remove_close_to_wolf(moves)
                if len(moves) > 0:
                    print(moves)
                    moves = moves[0]


        # nie mozna sie ruszyc ta na samym dole
        else:
            if len(self.sheep_block_wolf()) > 0:
                print('ta ktora zablokuje')
                print(moves)
                moves = self.sheep_block_wolf()
                moves = moves[0]
            else:
                # wszystkie dostepne
                moves = self.sheep_moves()
                # nie te ktore sa blisko wilka
                moves = self.remove_close_to_wolf(moves)
                print(moves)
                if len(moves) > 0:
                    print(moves)
                    moves = moves[0]

        print('!!!!!')
        chosen_move = moves
        print(chosen_move)

        # sheep_random_moves = []
        # for sh in range(0, 4):
        #     for sheep_move in self.get_possible_moves(sh):
        #         sheep_random_moves.append([sh, sheep_move])
        # chosen_move = random.choice(sheep_random_moves)
        #
        self.move_player(chosen_move[1][0], chosen_move[1][1], chosen_move[0])

    def lowest_move(self, moves):

        chosen_move_lowest = ()
        current_l = 100

        for mov in moves:
            p = self.points(mov)
            if p < current_l:
                current_l = p
                chosen_move_lowest = mov

        return chosen_move_lowest

    def highest_move(self, moves):

        chosen_move_highest = ()
        current_h = -1

        for mov in moves:
            p = self.points(mov)
            if p > current_h:
                current_h = p
                chosen_move_highest = mov

        return chosen_move_highest

    def closest_to_wolf(self, sh_moves):
        # punkty wilka
        self.points(self.wolf)
        c_mov = []

        current = -1
        for mov in sh_moves:
            p = self.points(mov[1])
            if p > current:
                current = p
                c_mov = mov

        return c_mov

    # owce blisko wilka
    # [[1, (3, 3)]]
    def sheep_close_to_wolf(self):
        sheeps_positions = self.sheep_positions()

        sheep_close_to_wolf = []

        #   | 0 |
        # 1 |   | 1
        #
        for sheep in sheeps_positions:
            if (sheep[1][0] == self.wolf[0] + 1 and sheep[1][1] == self.wolf[1] + 1) or (
                    sheep[1][0] == self.wolf[0] - 1 and sheep[1][1] == self.wolf[1] + 1):
                sheep_close_to_wolf.append(sheep[0])

        return sheep_close_to_wolf

    # usuniecie z ruchow tych ktore sa blisko wilka
    # zwraca liste sheep_moves bez tych ktore sa blikso wilka
    def remove_close_to_wolf(self, sh_moves):
        sh_close = self.sheep_close_to_wolf()

        result = [x for x in sh_moves if x[0] not in sh_close]

        return result

    # wybranie ruchu tych ktora moga zablokowac wilka
    def sheep_block_wolf(self):
        sh_moves = self.sheep_moves()
        can_block = []
        for sh in sh_moves:
            if sh[1] in self.get_possible_moves(4):
                can_block.append(sh)
        return can_block

    # wybranie ruchu
    def wolf_no_block(self):

        sh_moves = self.sheep_block_wolf()

        moves = []

        for mov in self.get_possible_moves(4):
            for sh_mov in sh_moves:
                if mov != sh_mov[1]:
                    moves.append(mov)

        return moves

    # ruchy dla owiec ktroe sa najnizej
    def sheep_lowest(self):
        # pozycje wszytkich owiec
        sheep = self.sheep_positions()
        lowest = [-1, (-1, -1)]
        result = []

        # najnizsza
        for sh in sheep:
            if sh[1][1] >= lowest[1][1]:
                lowest = sh

        # na rownym poziomie z najnizsza
        for sh in sheep:
            if sh[1][1] == lowest[1][1]:
                result.append(sh)

        # ruchy dla najnizszych owiec
        moves = []
        for sh in result:
            for sh_move in self.get_possible_moves(sh[0]):
                moves.append([sh[0], sh_move])

        return moves

    # ruchy dla owiec z dostepnym jednym ruchem
    def sheep_with_one_move(self, sh_moves):
        sheep_0_moves = []
        sheep_1_moves = []
        sheep_2_moves = []
        sheep_3_moves = []

        for sheep in sh_moves:
            if sheep[0] == 0:
                sheep_0_moves.append(sheep)
            if sheep[0] == 1:
                sheep_1_moves.append(sheep)
            if sheep[0] == 2:
                sheep_2_moves.append(sheep)
            if sheep[0] == 3:
                sheep_3_moves.append(sheep)

        with_one_move = []
        if 0 < len(sheep_0_moves) < 2:
            with_one_move.append(sheep_0_moves[0])
        if 0 < len(sheep_1_moves) < 2:
            with_one_move.append(sheep_1_moves[0])
        if 0 < len(sheep_2_moves) < 2:
            with_one_move.append(sheep_2_moves[0])
        if 0 < len(sheep_3_moves) < 2:
            with_one_move.append(sheep_3_moves[0])

        return with_one_move

    # oblicz punkty dla ruchu
    def points(self, m):
        p = m[0] + (m[1] * 10)
        return p

    # pozycje wszystkich owiec na planszy
    # [[0, (1, 7)], [1, (3, 7)], [2, (5, 7)], [3, (7, 7)]]
    def sheep_positions(self):
        sheeps_positions = []
        for i in range(0, 4):
            sheeps_positions.append([i, self.sheep[i]])

        return sheeps_positions

    # wszystkie mozliwe ruchy dla owiec
    def sheep_moves(self):
        sh_moves = []
        for sheep in range(0, 4):
            for sheep_move in self.get_possible_moves(sheep):
                sh_moves.append([sheep, sheep_move])

        return sh_moves

    # wszystkie mozliwe ruchy dla wilka
    def wolf_moves(self):
        w_moves = []
        for wolf_move in self.get_possible_moves(4):
            w_moves.append(wolf_move)

        return w_moves

    def did_wolf_win(self):
        return self.wolf[1] == 7 or (self.wolf[1] >= self.sheep[0][1] and self.wolf[1] >= self.sheep[1][1] and
                                     self.wolf[1] >= self.sheep[2][1] and self.wolf[1] >= self.sheep[3][1])

    def did_sheep_win(self):
        return len(self.get_possible_moves(4)) == 0

    def check_win(self):
        if self.did_wolf_win():
            self.database.wolf_won()
            return 1
        if self.did_sheep_win():
            self.database.sheep_won()
            return 1

        return None

    # 0-3 owce id , 4 wilk id
    def move_player(self, x, y, player_id):
        turn = int(self.database.select_whose_turn())
        possible_moves = self.get_possible_moves(player_id)
        player_move = (x, y)

        if player_id == 4 and turn == 0:
            if player_move in possible_moves:
                self.database.move(x, y, player_id)
                self.board[x][y] = '4'
                turn += 1
                turn %= 2
                self.database.next_turn(turn)
        else:
            if player_id in range(0, 4):
                self.database.move(x, y, player_id)
                self.board[x][y] = player_id
                turn += 1
                turn %= 2
                self.database.next_turn(turn)

    # mozliwe ruchy dla pionka
    def get_possible_moves(self, player_id):
        possible_directions = []
        if player_id == 4:
            player = self.wolf
            for d in self.directions:
                # nowy kierunek
                new_dir = (player[0] + d[0], player[1] + d[1])
                # czy nie wychodzi poza plansze i czy pole jest wolne
                if 0 <= new_dir[0] < 8 and 0 <= new_dir[1] < 8 and self.check_if_free(new_dir[0], new_dir[1]):
                    possible_directions.append(new_dir)
        else:
            player = self.sheep[player_id]
            for d in [(1, -1), (-1, -1)]:
                # nowy kierunek
                new_dir = (player[0] + d[0], player[1] + d[1])
                if 0 <= new_dir[0] < 8 and 0 <= new_dir[1] < 8 and self.check_if_free(new_dir[0], new_dir[1]):
                    possible_directions.append(new_dir)
        return possible_directions

    # czy na podane wspolrzedne nie sa zajete
    def check_if_free(self, x, y):
        is_free = True
        is_free = is_free and not (self.wolf[0] == x and self.wolf[1] == y)
        for i in range(0, 4):
            is_free = is_free and not (self.sheep[i][0] == x and self.sheep[i][1] == y)
        return is_free
