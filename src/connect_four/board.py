import random

class Board:
    def __init__(self):
        # 7 columns, 6 rows
        self.board = [[0 for _ in range(6)] for _ in range(7)] # 0 is empty, 1 is player 1, 2 is player 2
        self.turn = 1

        self.move_list = []

        self.zobrist_table = [[[random.randint(1, 2**64 - 1) for _ in range(3)] for _ in range(6)] for _ in range(7)]
        self.hash_value = self.compute_hash()

    def compute_hash(self):
        hash_value = 0
        for column in range(7):
            for row in range(6):
                if self.board[column][row] != 0:
                    piece = self.board[column][row]
                    hash_value ^= self.zobrist_table[column][row][piece]
        return hash_value
    
    def count_threats(self):

        threats = {1: 0, 2: 0}

        def check_line(segment, player):
            count = segment.count(player)
            if count == 3 and segment.count(0) == 1:
                return 1
            return 0

        # check horizontal threats
        for row in range(6):
            for col in range(4):
                segment = [self.board[c][row] for c in range(col, col + 4)]
                threats[1] += check_line(segment, 1)
                threats[2] += check_line(segment, 2)

        # check vertical threats
        for col in range(7):
            for row in range(3):
                segment = [self.board[col][r] for r in range(row, row + 4)]
                threats[1] += check_line(segment, 1)
                threats[2] += check_line(segment, 2)

        # check diagonal threats (top-left to bottom-right)
        for col in range(4):
            for row in range(3):
                segment = [self.board[col + i][row + i] for i in range(4)]
                threats[1] += check_line(segment, 1)
                threats[2] += check_line(segment, 2)

        # check diagonal threats (bottom-left to top-right)
        for col in range(4):
            for row in range(3, 6):
                segment = [self.board[col + i][row - i] for i in range(4)]
                threats[1] += check_line(segment, 1)
                threats[2] += check_line(segment, 2)

        return threats

    def is_valid_move(self, column):
        return 0 in self.board[column]
    
    def get_row(self, column):
        # get the row where the piece will be placed
        for row in range(6):
            if self.board[column][row] == 0:
                return row

    def drop_piece(self, column):
        for row in range(6):
            if self.board[column][row] == 0:
                self.board[column][row] = self.turn
                self.hash_value ^= self.zobrist_table[column][row][self.turn]
                break

        self.move_list.append((column, row))
        self.turn = 1 if self.turn == 2 else 2

    def undo_move(self):
        column, row = self.move_list.pop()
        self.hash_value ^= self.zobrist_table[column][row][self.board[column][row]]
        self.board[column][row] = 0

        self.turn = 1 if self.turn == 2 else 2
                
    def get_legal_moves(self):
        return [column for column in range(7) if 0 in self.board[column]]
    
    def check_winner(self):
        # check rows
        for row in range(6):
            for column in range(4):
                if self.board[column][row] == self.board[column + 1][row] == self.board[column + 2][row] == self.board[column + 3][row] != 0:
                    return self.board[column][row]
        
        # check columns
        for column in range(7):
            for row in range(3):
                if self.board[column][row] == self.board[column][row + 1] == self.board[column][row + 2] == self.board[column][row + 3] != 0:
                    return self.board[column][row]
        
        # check diagonal (top-left to bottom-right)
        for column in range(4):
            for row in range(3):
                if self.board[column][row] == self.board[column + 1][row + 1] == self.board[column + 2][row + 2] == self.board[column + 3][row + 3] != 0:
                    return self.board[column][row]
        
        # check diagonal (bottom-left to top-right)
        for column in range(4):
            for row in range(3, 6):
                if self.board[column][row] == self.board[column + 1][row - 1] == self.board[column + 2][row - 2] == self.board[column + 3][row - 3] != 0:
                    return self.board[column][row]
        
        return 0
    
    def is_full(self):
        return all(0 not in column for column in self.board)
    
    def __repr__(self):
        board = ""
        for row in range(6, 0, -1):
            for column in range(7):
                board += "X " if self.board[column][row - 1] == 1 else "O " if self.board[column][row - 1] == 2 else ". "
            board += "\n"
        # print column numbers
        for column in range(7):
            board += str(column) + " "
            
        return board