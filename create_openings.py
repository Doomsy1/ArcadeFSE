import chess.pgn
from src.chess.board import Piece

ELO_THRESHOLD = 2000
MIN_GAME_LENGTH = 10

Openings = {}
# (start, end, start_piece, captured_piece, promotion_piece, castling, en_passant_flag)
def create_formatted_move(board: chess.Board, move: chess.Move):
    start = move.from_square
    end = move.to_square

    start_piece_symbol = board.piece_at(start)
    if start_piece_symbol is None:
        start_piece = 0
    else:
        start_piece = Piece.get_piece_from_char(start_piece_symbol)

    captured_piece_symbol = board.piece_at(end)
    if captured_piece_symbol is None:
        captured_piece = 0
    else:
        captured_piece = Piece.get_piece_from_char(captured_piece_symbol)

    promotion_piece = move.promotion if move.promotion is not None else 0
    castling = 1 if board.is_castling(move) else 0
    en_passant_flag = 1 if board.is_en_passant(move) else 0
    
    formatted_move = (start, end, start_piece, captured_piece, promotion_piece, castling, en_passant_flag)

    return formatted_move

def process_pgn(file_path):
    with open(file_path, encoding='utf-8') as pgn_file:
        game_count = 0
        while True:
            game = chess.pgn.read_game(pgn_file)
            
            # if there are no more games, break
            if game is None:
                break

            # if the game is too short, skip it
            move_count = sum(1 for _ in game.mainline_moves())
            if move_count < MIN_GAME_LENGTH:
                continue

            # if the game is not rated, skip it
            white_elo = game.headers["WhiteElo"]
            black_elo = game.headers["BlackElo"]
            if white_elo is None or black_elo is None:
                continue

            # if the elo is unsure, skip it
            if "?" in white_elo or "?" in black_elo:
                continue

            # if the elo is below the threshold, skip it
            white_elo = int(white_elo)
            black_elo = int(black_elo)
            if white_elo < ELO_THRESHOLD or black_elo < ELO_THRESHOLD:
                continue

            # if the opening is not defined, skip it
            opening = game.headers["Opening"]
            if opening is None:
                continue

            game_count += 1
            board = game.board()

            move_count = 0
            for move in game.mainline_moves():
                move_count += 1
                fen = board.fen()
                formatted_move = create_formatted_move(board, move)
                game_result = game.headers["Result"]
                print(game_result)

                
            input("Enter to continue...")

            
            

            


process_pgn("lichess_db_standard_rated_2013-01.pgn")
