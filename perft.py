import time
import csv
from src.chess.board import Board
import cProfile
import pstats
import io

def count_positions(board: Board, depth):
    if depth == 0:
        return 1
    count = 0

    legal_moves = board.generate_legal_moves()
    # known_legal_moves = board.known_generate_legal_moves()
    # for move in known_legal_moves:
    #     if move not in legal_moves:
    #         print(board.create_fen())
    #         print(move, "not in generated legal moves")
    #         input()
    #         print("ok")
    for move in legal_moves:
        # if move not in known_legal_moves:
        #     print(board.create_fen())
        #     print(move, "not in known legal moves")
        #     input()
        #     print("ok")
        board.make_move(move)
        count += count_positions(board, depth - 1)
        board.undo_move()
    return count

def main():
    board = Board()

    for depth in range(1, 5):
        start_time = time.time()
        count = count_positions(board, depth)
        duration = time.time() - start_time

        print(f"Depth: {depth}, Positions: {count}, Duration: {duration:.2f} sec")
    
    # expected output:
    # Depth: 1, Positions: 20
    # Depth: 2, Positions: 400
    # Depth: 3, Positions: 8902
    # Depth: 4, Positions: 197281
    # Depth: 5, Positions: 4865609
    # Depth: 6, Positions: 119060324


if __name__ == "__main__":
    pr = cProfile.Profile()
    pr.enable()
    main()
    pr.disable()
    
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s)
    ps.sort_stats('cumulative')
    ps.print_stats()
    
    with open('benchmark.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Function', 'Calls', 'Total Time', 'Per Call', 'Cumulative Time', 'Per Call (cumulative)'])
        
        sorted_stats = sorted(ps.stats.items(), key=lambda x: x[1][3], reverse=True)
        
        for func, stats in sorted_stats:
            cc, nc, tt, ct, callers = stats
            per_call = tt / nc if nc else 0
            cum_per_call = ct / nc if nc else 0
            func_str = pstats.func_std_string(func)
            writer.writerow([func_str, nc, tt, per_call, ct, cum_per_call])