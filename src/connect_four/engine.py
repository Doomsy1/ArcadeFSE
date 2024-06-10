from src.connect_four.board import Board
# from board import Board

from collections import OrderedDict
import random
import time

POSITIVE_INFINITY = float("inf")
NEGATIVE_INFINITY = float("-inf")

THREAT_VALUE = 100
CENTER_CONTROL_VALUE = 10


class TranspositionTable:
    def __init__(self, capacity = 10e6):
        self.table = OrderedDict()
        self.capacity = capacity

    def get(self, key):
        if key in self.table:
            self.table.move_to_end(key)
            return self.table[key]
        return None

    def put(self, key, value):
        if key in self.table:
            self.table.move_to_end(key)
        elif len(self.table) >= self.capacity:
            self.table.popitem(last=False)
        self.table[key] = value

# player 1 is the maximizing player
# player 2 is the minimizing player
class Engine:
    def __init__(self, board: Board, time_limit_ms=5000):
        self.board = board
        self.time_limit_ms = time_limit_ms

        self.transposition_table = TranspositionTable(capacity=10e6)

    def update_board(self, board: Board):
        self.board = board

    def evaluate_center_control(self):
        return 0
        # center_column = [self.board[3][row] for row in range(6)]
        # score = center_column.count(1) - center_column.count(2)
        # return score * CENTER_CONTROL_VALUE

    def evaluate(self):
        winner = self.board.check_winner()
        if winner == 1:
            return POSITIVE_INFINITY
        if winner == 2:
            return NEGATIVE_INFINITY
        
        score = 0

        # check threats
        threat_counts = self.board.count_threats()
        score = (threat_counts[1] - threat_counts[2]) * THREAT_VALUE

        # check center control
        score += self.evaluate_center_control()
        
        return score

    def minimax(self, depth, alpha, beta):
        key = (self.board.hash_value, depth)
        cached = self.transposition_table.get(key)
        if cached is not None:
            return cached
        
        winner = self.board.check_winner()
        if winner or self.board.is_full() or depth == 0:
            score = self.evaluate()
            self.transposition_table.put(key, score)
            return score
        
        if self.board.turn == 1:
            best_score = NEGATIVE_INFINITY
            for move in self.board.get_legal_moves():
                self.board.drop_piece(move)
                score = self.minimax(depth - 1, alpha, beta)
                self.board.undo_move()
                best_score = max(best_score, score)
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break
        else:
            best_score = POSITIVE_INFINITY
            for move in self.board.get_legal_moves():
                self.board.drop_piece(move)
                score = self.minimax(depth - 1, alpha, beta)
                self.board.undo_move()
                best_score = min(best_score, score)
                beta = min(beta, best_score)
                if beta <= alpha:
                    break

        self.transposition_table.put(key, best_score)
        return best_score
        
    def get_best_move(self, depth):
        best_move = None
        alpha = NEGATIVE_INFINITY
        beta = POSITIVE_INFINITY

        if self.board.turn == 1:
            best_score = NEGATIVE_INFINITY
            for move in self.board.get_legal_moves():
                self.board.drop_piece(move)
                score = self.minimax(depth - 1, alpha, beta)
                self.board.undo_move()

                if score >= best_score:
                    best_score = score
                    best_move = move

        else:
            best_score = POSITIVE_INFINITY
            for move in self.board.get_legal_moves():
                self.board.drop_piece(move)
                score = self.minimax(depth - 1, alpha, beta)
                self.board.undo_move()

                if score <= best_score:
                    best_score = score
                    best_move = move

        return best_move
    
    # result_container = [move, Final] 
    # Final: search finished or not
    def iterative_deepening(self, result_container: list):
        start_time = time.time()

        moves = self.board.get_legal_moves()
        if len(moves) == 1:
            result_container.append((moves[0], True))
            return

        best_move = None
        depth = 1
        while time.time() - start_time < self.time_limit_ms / 1000:
            best_move = self.get_best_move(depth)
            result_container.append((best_move, False))
            # print(f"Depth reached: {depth} in {time.time() - start_time:.2f} seconds, best move: {best_move}")
            depth += 1

        # print(f"Depth reached: {depth - 1} in {time.time() - start_time:.2f} seconds")
        # print(f"Best move: {best_move}")
        result_container.append((best_move, True))
        


if __name__ == "__main__":
    board = Board()
    engine = Engine(board, time_limit_ms=5000)

    while True:
        print(board)
        if board.check_winner() == 1:
            print("Player 1 wins!")
            break
        if board.check_winner() == 2:
            print("Player 2 wins!")
            break
        if board.is_full():
            print("It's a tie!")
            break

        if board.turn == 1:
            move = input("Player 1, enter your move: ")
        else:

            result_container = []
            engine.iterative_deepening(result_container)
            while result_container[-1][1] == False:
                pass
            move = result_container[-1][0]
            print(f"Player 2 plays {move}")

        if move == "u":
            board.undo_move()
        else:
            board.drop_piece(int(move))