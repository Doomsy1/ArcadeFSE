from collections import OrderedDict

POSITIVE_INFINITY = float("inf")
NEGATIVE_INFINITY = float("-inf")

from board import Board

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
    def __init__(self, board):
        self.board = board

        self.transposition_table = TranspositionTable(capacity=10e6)

    def evaluate(self):
        winner = self.board.check_winner()
        if winner == 1:
            return POSITIVE_INFINITY
        if winner == 2:
            return NEGATIVE_INFINITY
        return 0

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

                if score > best_score:
                    best_score = score
                    best_move = move

        else:
            best_score = POSITIVE_INFINITY
            for move in self.board.get_legal_moves():
                self.board.drop_piece(move)
                score = self.minimax(depth - 1, alpha, beta)
                self.board.undo_move()

                if score < best_score:
                    best_score = score
                    best_move = move

        return best_move
        


if __name__ == "__main__":
    board = Board()
    engine = Engine(board)

    while True:
        print(board)
        print(board.hash_value)
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
            move = engine.get_best_move(10)
            print(f"Player 2 plays {move}")

        if move == "u":
            board.undo_move()
        else:
            board.drop_piece(int(move))