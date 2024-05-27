from src.chess.board import Piece

PSQT = {
    "Opening": {
        Piece.white | Piece.pawn: [
            [  0,   0,   0,   0,   0,   0,   0,   0],
            [150, 150, 150, 150, 150, 150, 150, 150],
            [110, 110, 120, 130, 130, 120, 110, 110],
            [105, 105, 110, 125, 125, 110, 105, 105],
            [100, 100, 100, 120, 120, 100, 100, 100],
            [105,  95,  90, 100, 100,  90,  95, 105],
            [105, 110, 110,  80,  80, 110, 110, 105],
            [100, 100, 100, 100, 100, 100, 100, 100]
        ],
        Piece.white | Piece.knight: [
            [250, 260, 270, 270, 270, 270, 260, 250],
            [260, 280, 300, 300, 300, 300, 280, 260],
            [270, 300, 310, 315, 315, 310, 300, 270],
            [270, 305, 315, 320, 320, 315, 305, 270],
            [270, 300, 315, 320, 320, 315, 300, 270],
            [270, 305, 310, 315, 315, 310, 305, 270],
            [260, 280, 300, 305, 305, 300, 280, 260],
            [250, 260, 270, 270, 270, 270, 260, 250]
        ],
        Piece.white | Piece.bishop: [
            [280, 290, 290, 290, 290, 290, 290, 280],
            [290, 300, 300, 300, 300, 300, 300, 290],
            [290, 300, 305, 310, 310, 305, 300, 290],
            [290, 305, 305, 310, 310, 305, 305, 290],
            [290, 300, 310, 310, 310, 310, 300, 290],
            [290, 310, 310, 310, 310, 310, 310, 290],
            [290, 305, 300, 300, 300, 300, 305, 290],
            [280, 290, 290, 290, 290, 290, 290, 280]
        ],
        Piece.white | Piece.rook: [
            [500, 500, 500, 500, 500, 500, 500, 500],
            [505, 510, 510, 510, 510, 510, 510, 505],
            [495, 500, 500, 500, 500, 500, 500, 495],
            [495, 500, 500, 500, 500, 500, 500, 495],
            [495, 500, 500, 500, 500, 500, 500, 495],
            [495, 500, 500, 500, 500, 500, 500, 495],
            [495, 500, 500, 500, 500, 500, 500, 495],
            [500, 500, 500, 505, 505, 500, 500, 500]
        ],
        Piece.white | Piece.queen: [
            [880, 890, 890, 895, 895, 890, 890, 880],
            [890, 900, 900, 900, 900, 900, 900, 890],
            [890, 900, 905, 905, 905, 905, 900, 890],
            [895, 900, 905, 905, 905, 905, 900, 895],
            [895, 900, 905, 905, 905, 905, 900, 895],
            [890, 900, 905, 905, 905, 905, 900, 890],
            [890, 900, 900, 900, 900, 900, 900, 890],
            [880, 890, 890, 895, 895, 890, 890, 880]
        ],
        Piece.white | Piece.king: [
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-30, -40, -40, -50, -50, -40, -40, -30],
            [-20, -30, -30, -40, -40, -30, -30, -20],
            [-10, -20, -20, -20, -20, -20, -20, -10],
            [ 20,  20,   0,   0,   0,   0,  20,  20],
            [ 20,  30,  10,   0,   0,  10,  30,  20]
        ]
        },
    "Endgame": {
        Piece.white | Piece.pawn: [
            [  0,   0,   0,   0,   0,   0,   0,   0],
            [170, 170, 170, 170, 170, 170, 170, 170],
            [150, 150, 150, 150, 150, 150, 150, 150],
            [140, 140, 140, 140, 140, 140, 140, 140],
            [130, 130, 130, 130, 130, 130, 130, 130],
            [120, 120, 120, 120, 120, 120, 120, 120],
            [110, 110, 110, 110, 110, 110, 110, 110],
            [100, 100, 100, 100, 100, 100, 100, 100]
        ],
        Piece.white | Piece.knight: [
            [250, 260, 270, 270, 270, 270, 260, 250],
            [260, 280, 300, 300, 300, 300, 280, 260],
            [270, 300, 310, 315, 315, 310, 300, 270],
            [270, 305, 315, 320, 320, 315, 305, 270],
            [270, 300, 315, 320, 320, 315, 300, 270],
            [270, 305, 310, 315, 315, 310, 305, 270],
            [260, 280, 300, 305, 305, 300, 280, 260],
            [250, 260, 270, 270, 270, 270, 260, 250]
        ],
        Piece.white | Piece.bishop: [
            [280, 290, 290, 290, 290, 290, 290, 280],
            [290, 300, 300, 300, 300, 300, 300, 290],
            [290, 300, 310, 315, 315, 310, 300, 290],
            [290, 310, 315, 320, 320, 315, 310, 290],
            [290, 300, 315, 320, 320, 315, 300, 290],
            [290, 310, 310, 315, 315, 310, 310, 290],
            [290, 315, 300, 300, 300, 300, 315, 290],
            [280, 290, 290, 290, 290, 290, 290, 280]
        ],
        Piece.white | Piece.rook: [
            [500, 500, 500, 505, 505, 500, 500, 500],
            [495, 500, 500, 500, 500, 500, 500, 495],
            [495, 500, 500, 500, 500, 500, 500, 495],
            [495, 500, 500, 500, 500, 500, 500, 495],
            [495, 500, 500, 500, 500, 500, 500, 495],
            [495, 500, 500, 500, 500, 500, 500, 495],
            [505, 510, 510, 510, 510, 510, 510, 505],
            [500, 500, 500, 505, 505, 500, 500, 500]
        ],
        Piece.white | Piece.queen: [
            [880, 890, 890, 895, 895, 890, 890, 880],
            [890, 900, 900, 900, 900, 900, 900, 890],
            [890, 900, 905, 905, 905, 905, 900, 890],
            [895, 900, 905, 905, 905, 905, 900, 895],
            [895, 900, 905, 905, 905, 905, 900, 895],
            [890, 900, 905, 905, 905, 905, 900, 890],
            [890, 900, 900, 900, 900, 900, 900, 890],
            [880, 890, 890, 895, 895, 890, 890, 880]
        ],
        Piece.white | Piece.king: [
            [-50, -40, -30, -20, -20, -30, -40, -50],
            [-30, -20, -10,   0,   0, -10, -20, -30],
            [-30, -10,  20,  30,  30,  20, -10, -30],
            [-30, -10,  30,  40,  40,  30, -10, -30],
            [-30, -10,  30,  40,  40,  30, -10, -30],
            [-30, -10,  20,  30,  30,  20, -10, -30],
            [-30, -30,   0,   0,   0,   0, -30, -30],
            [-50, -30, -30, -30, -30, -30, -30, -50]
        ]
    }
}

# add black pieces
for phase in PSQT: # Opening, Endgame
    for piece in list(PSQT[phase].keys()):
        table = PSQT[phase][piece]

        black_table = []
        for rank in table[::-1]:
            black_rank = [-score for score in rank]
            black_table.append(black_rank)

        piece_type = Piece.get_type(piece)
        PSQT[phase][piece_type | Piece.black] = black_table


PHASE_WEIGHTS = {
    Piece.pawn: 0,
    Piece.knight: 1,
    Piece.bishop: 1,
    Piece.rook: 2,
    Piece.queen: 4,
    Piece.king: 0
}

TOTAL_PHASE = (
    8 * PHASE_WEIGHTS[Piece.pawn] +
    2 * PHASE_WEIGHTS[Piece.knight] +
    2 * PHASE_WEIGHTS[Piece.bishop] +
    2 * PHASE_WEIGHTS[Piece.rook] +
    1 * PHASE_WEIGHTS[Piece.queen] +
    1 * PHASE_WEIGHTS[Piece.king]
)