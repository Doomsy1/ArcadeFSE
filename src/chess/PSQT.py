from src.chess.PSQT_2D import PSQT_2D
from src.chess.board import Piece

PSQT = {}

for phase in PSQT_2D:
    PSQT[phase] = {}
    for piece in PSQT_2D[phase]:
        table = PSQT_2D[phase][piece]

        table_1d = []
        # convert the 2d list into a tuple
        for rank in table[::-1]:
            table_1d.extend(rank)

        table_tuple = tuple(table_1d)

        PSQT[phase][piece] = table_tuple

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