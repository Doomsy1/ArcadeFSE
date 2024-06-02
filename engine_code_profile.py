import cProfile
import csv
import io
import pstats
from src.chess.engine import Engine
from src.chess.board import Board


if __name__ == "__main__":
    pr = cProfile.Profile()
    b = Board()
    engine = Engine(b)
    b.load_fen('2r3k1/p4p2/3Rp2p/1p2P1pK/8/1P4P1/P3Q2P/1q6 b - - 0 1')
    engine.update_board(b)

    pr.enable()
    engine.iterative_deepening([])
    pr.disable()
    
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s)
    ps.sort_stats('cumulative')
    ps.print_stats()
    
    with open('engine_profile.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Function', 'Calls', 'Total Time', 'Per Call', 'Cumulative Time', 'Per Call (cumulative)'])
        
        sorted_stats = sorted(ps.stats.items(), key=lambda x: x[1][3], reverse=True)
        
        for func, stats in sorted_stats:
            cc, nc, tt, ct, callers = stats
            per_call = tt / nc if nc else 0
            cum_per_call = ct / nc if nc else 0
            func_str = pstats.func_std_string(func)
            writer.writerow([func_str, nc, tt, per_call, ct, cum_per_call])


