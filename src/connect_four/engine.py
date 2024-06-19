from src.connect_four.board import Board
# from board import Board
from concurrent.futures import ThreadPoolExecutor

from collections import OrderedDict
import time

POSITIVE_INFINITY = 9999999
NEGATIVE_INFINITY = -9999999

STRONG_THREAT_VALUE = 1000
WEAK_THREAT_VALUE = 100


CENTER_HEURISTIC_WEIGHT = 2


class TranspositionTable:
    def __init__(self, capacity = 10e3):
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

        self.history_table = {}

        self.transposition_table = TranspositionTable(capacity=10e6)

    def update_board(self, board: Board):
        self.board = board.copy()

    def evaluate_center_control(self):
        # count num 

        pass

    def get_ordered_moves(self):
        moves = self.board.get_legal_moves()

        move_scores = []

        for move in moves:
            history_score = lambda move: self.history_table.get(move, 0)

            # center moves first (3, 2, 4, 1, 5, 0, 6)
            center_score = 3 - abs(move - 3)

            move_score = history_score(move) + CENTER_HEURISTIC_WEIGHT * center_score

            move_scores.append((move, move_score))

        move_scores.sort(key=lambda x: x[1], reverse=True)

    
        return [move for move, _ in move_scores]

    def update_history_score(self, move, depth):
        if move not in self.history_table:
            self.history_table[move] = 0
        self.history_table[move] += 3 ** depth

    def evaluate_threats(self):
        # player 1 threats are strong on rows that are odd
        # player 2 threats are strong on rows that are even

        threat_value = 0
        threat_map = self.board.create_threat_map()

        # go through the threat map and evaluate the threats
        for column in range(7):
            for row in range(6):
                if threat_map[column][row][0]: # player 1 threat
                    parity = row % 2
                    if parity == 0:
                        threat_value += STRONG_THREAT_VALUE
                    else:
                        threat_value += WEAK_THREAT_VALUE

                if threat_map[column][row][1]: # player 2 threat
                    parity = row % 2
                    if parity == 1:
                        threat_value -= STRONG_THREAT_VALUE
                    else:
                        threat_value -= WEAK_THREAT_VALUE

        return threat_value

    def evaluate(self):
        score = 0

        # threats
        score += self.evaluate_threats()
        
        return score

    def minimax(self, depth, alpha, beta):
        self.num_evaluations += 1

        # TOFIX: interference
        # key = (self.board.hash_board(), depth)
        # cached = self.transposition_table.get(key)
        # if cached is not None:
        #     return cached
        
        winner = self.board.check_winner()
        if winner == 1:
            score = POSITIVE_INFINITY - (42 - depth)
            # self.transposition_table.put(key, score)
            return score
        elif winner == 2:
            score = NEGATIVE_INFINITY + (42 - depth)
            # self.transposition_table.put(key, score)
            return score
        elif self.board.is_full():
            score = 0
            # self.transposition_table.put(key, score)
            return score
        elif depth == 0:
            score = self.evaluate()
            # self.transposition_table.put(key, score)
            return score
        
        if self.board.turn == 1:
            best_score = NEGATIVE_INFINITY
            for move in self.get_ordered_moves():
                self.board.drop_piece(move)
                score = self.minimax(depth - 1, alpha, beta)
                self.board.undo_move()
                best_score = max(best_score, score)
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    self.update_history_score(move, depth)
                    break
        else:
            best_score = POSITIVE_INFINITY
            for move in self.get_ordered_moves():
                self.board.drop_piece(move)
                score = self.minimax(depth - 1, alpha, beta)
                self.board.undo_move()
                best_score = min(best_score, score)
                beta = min(beta, best_score)
                if beta <= alpha:
                    self.update_history_score(move, depth)
                    break

        # self.transposition_table.put(key, best_score)
        return best_score
        
    def get_best_move(self, depth):
        best_move = None
        alpha = NEGATIVE_INFINITY
        beta = POSITIVE_INFINITY

        if self.board.turn == 1:
            best_score = NEGATIVE_INFINITY
            for move in self.get_ordered_moves():
                self.board.drop_piece(move)
                score = self.minimax(depth - 1, alpha, beta)
                self.board.undo_move()

                if score >= best_score:
                    best_score = score
                    best_move = move

        else:
            best_score = POSITIVE_INFINITY
            for move in self.get_ordered_moves():
                self.board.drop_piece(move)
                score = self.minimax(depth - 1, alpha, beta)
                self.board.undo_move()

                if score <= best_score:
                    best_score = score
                    best_move = move

        return best_move, best_score
    
    # result_container = [move, Final] 
    # Final: search finished or not
    def iterative_deepening(self, result_container: list):
        self.num_evaluations = 0

        print(f"What engine sees:\n{self.board}")

        start_time = time.time()

        moves = self.get_ordered_moves()
        if len(moves) == 1:
            result_container.append((moves[0], True))
            return

        best_move = None
        depth = 1
        while time.time() - start_time < self.time_limit_ms / 1000:
            if depth > 40:
                break
            
            best_move, score = self.get_best_move(depth)
            if best_move == POSITIVE_INFINITY or best_move == NEGATIVE_INFINITY:
                break

            result_container.append((best_move, False))
            print(f"Depth {depth} finished in {time.time() - start_time:.2f} seconds | Best move: {best_move} | Score: {score} | Evaluations: {self.num_evaluations}")
            depth += 1

        print(f"Best move: {best_move} with score {score}")
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