from src.chess.PSQT_2D import PSQT_2D
from src.chess.board import Piece



PSQT = {}

for phase in PSQT_2D:
    PSQT[phase] = {}
    for piece in PSQT_2D[phase]:
        piece_type = Piece.get_type(piece)
        piece_value = Piece.get_value(piece_type)
        piece_value *= -1 if Piece.get_color(piece) == Piece.black else 1
        
        table = PSQT_2D[phase][piece]

        table_1d = []
        # convert the 2d list into a tuple
        for rank in table[::-1]:
            # add piece values to the rank
            rank = [piece_value + square for square in rank]
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
    16 * PHASE_WEIGHTS[Piece.pawn] +
    4 * PHASE_WEIGHTS[Piece.knight] +
    4 * PHASE_WEIGHTS[Piece.bishop] +
    4 * PHASE_WEIGHTS[Piece.rook] +
    2 * PHASE_WEIGHTS[Piece.queen] +
    2 * PHASE_WEIGHTS[Piece.king]
)