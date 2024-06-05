import chess.pgn # do pip install python-chess
from src.chess.board import Piece, Board
import json

ELO_THRESHOLD = 2000
MIN_GAME_LENGTH = 10

Responses = {}
# (start, end, start_piece, captured_piece, promotion_piece, castling, en_passant_flag)
def create_formatted_move(board: chess.Board, move: chess.Move):
    start = move.from_square
    end = move.to_square

    # start_piece_symbol = board.piece_at(start).symbol() if board.piece_at(start) is not None else None
    # if start_piece_symbol is None:
    #     start_piece = 0
    # else:

    #     start_piece = Piece.get_piece_from_char(start_piece_symbol)

    # captured_piece_symbol = board.piece_at(end).symbol() if board.piece_at(end) is not None else None
    # if captured_piece_symbol is None:
    #     captured_piece = 0
    # else:
    #     captured_piece = Piece.get_piece_from_char(captured_piece_symbol)

    # promotion_piece = move.promotion if move.promotion is not None else 0
    # castling = 1 if board.is_castling(move) else 0
    # en_passant_flag = 1 if board.is_en_passant(move) else 0
    
    # TODO: make formatted move a tuple
    formatted_move = f"{start}, {end}"#, {start_piece}, {captured_piece}, {promotion_piece}, {castling}, {en_passant_flag}"

    return formatted_move

def process_pgn(pgn_file_path: str, export_file_path: str):
    b = Board()
    with open(pgn_file_path, encoding="utf-8") as pgn_file:
        game_count = 0
        while True:
            game = chess.pgn.read_game(pgn_file)
            
            # if there are no more games, break
            if game is None:
                break

            # # if the game is not rated, skip it
            # white_elo = game.headers["WhiteElo"]
            # black_elo = game.headers["BlackElo"]
            # if white_elo is None or black_elo is None:
            #     continue

            # # if the elo is unsure, skip it
            # if "?" in white_elo or "?" in black_elo:
            #     continue

            # # if the elo is below the threshold, skip it
            # white_elo = int(white_elo)
            # black_elo = int(black_elo)
            # if white_elo < ELO_THRESHOLD or black_elo < ELO_THRESHOLD:
            #     continue

            game_count += 1
            board = game.board()

            game_result = game.headers["Result"]
            turn = True # white's turn
            for move in game.mainline_moves():
                fen = board.fen()
                b.load_fen(fen)
                fen = b.create_fen()
                formatted_move = create_formatted_move(board, move)
                if fen not in Responses:
                    Responses[fen] = {formatted_move: 0}
                elif formatted_move not in Responses[fen]:
                    Responses[fen][formatted_move] = 0

                if game_result == "1-0":
                    Responses[fen][formatted_move] += 1
                elif game_result == "0-1":
                    Responses[fen][formatted_move] -= 1

                board.push(move)
                    
            print(f"Count: {game_count}\tResult: {game_result}")

        # export the responses to a json file
        with open(export_file_path, "w") as file:
            json.dump(Responses, file)      
            

            


process_pgn("Carlsen.pgn", "Carlsen_openings.json")
