import cProfile
import csv
import io
import pstats
from src.chess.board import Board
from src.chess.engine import Engine

def time_mate(engine: Engine, fen):
    engine.board.load_fen(fen)
    engine.iterative_deepening([])


mates = [
    '2r3k1/p4p2/3Rp2p/1p2P1pK/8/1P4P1/P3Q2P/1q6 b - - 0 1',
    '1k5r/pP3ppp/3p2b1/1BN1n3/1Q2P3/P1B5/KP3P1P/7q w - - 1 0',
    '3r4/pR2N3/2pkb3/5p2/8/2B5/qP3PPP/4R1K1 w - - 1 0',
    'R6R/1r3pp1/4p1kp/3pP3/1r2qPP1/7P/1P1Q3K/8 w - - 1 0',
    '4r1k1/5bpp/2p5/3pr3/8/1B3pPq/PPR2P2/2R2QK1 b - - 0 1',
    'r3k2r/ppp2Npp/1b5n/4p2b/2B1P2q/BQP2P2/P5PP/RN5K w kq - 1 0',
    '6k1/ppp2ppp/8/2n2K1P/2P2P1P/2Bpr3/PP4r1/4RR2 b - - 0 1',
    '8/2p3N1/6p1/5PB1/pp2Rn2/7k/P1p2K1P/3r4 w - - 1 0',
    '1k1r4/3b1p2/QP1b3p/1p1p4/3P2pN/1R4P1/KPPq1PP1/4r2R w - - 1 0',
    '7k/1p4R1/3bp2p/3p3N/p2P4/4NQPP/PP5K/2r1q3 w - - 1 0'
]

if __name__ == "__main__":
    pr = cProfile.Profile()
    b = Board()
    engine = Engine(b)

    pr.enable()
    for mate in mates:
        time_mate(engine, mate)
    pr.disable()
    
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s)
    ps.sort_stats('cumulative')
    ps.print_stats()
    
    # print total cumulative time
    print('Total cumulative time: ', ps.total_tt)

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


