import time
from src.chess.board import Board

def traverse_positions(board: Board, depth):
    if depth == 0:
        return 1
    count = 0

    legal_moves = board.generate_legal_moves()
    for move in legal_moves:
        board.make_move(move)
        count += traverse_positions(board, depth - 1)
        board.undo_move()
    return count


def main():
    board = Board()

    starting_time = time.time()

    count = traverse_positions(board, 4)
    
    duration = time.time() - starting_time

    print(f"Positions: {count}, Duration: {duration:.2f} sec, Positions per second: {count / duration:.0f}")

if __name__ == "__main__":
    main()