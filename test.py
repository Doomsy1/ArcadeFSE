from src.chess.board import Board, Piece
import time

if __name__ == "__main__":
    b = Board()

    num_trials = 10000
    start = time.time_ns()
    for _ in range(num_trials):
        b.generate_legal_moves()
    end = time.time_ns()

    print(f"Time per method call: {(end - start) // num_trials} ns")