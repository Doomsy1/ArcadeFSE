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

    for depth in range(1, 8):
        try:
            start_time = time.time_ns()
            count = traverse_positions(board, depth)
            duration = time.time_ns() - start_time

            try:
                result = f"Positions: {count}, Duration: {(duration / 1e9):.4f} seconds, Positions per second: {(count / (duration / 1e9)):.0f}\n"
            except ZeroDivisionError:
                result = f"Positions: {count}, Duration: {duration} ns, Positions per ns: {count}\n"
            
            with open('results.txt', 'a') as file:
                file.write(result)
            
            print(result.strip())

        except Exception as e:
            error_message = f"An error occurred at depth {depth}: {str(e)}\n"
            print(error_message)
            with open('results.txt', 'a') as file:
                file.write(error_message)

if __name__ == "__main__":
    main()