STARTING_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

piece_values = {
    'p': 1,
    'n': 3,
    'b': 3,
    'r': 5,
    'q': 9,
    'k': 1000
}

class Piece:
    def __init__(self, type, position):
        if type is not None:
            self.type = type.lower()
            # True if white, False if black
            self.is_white = type.isupper()
            self.value = piece_values[self.type]
            self.position = position
        else:
            self.type = None
            self.is_white = None
            self.value = 0
            self.position = position

    def __repr__(self):
        return self.type

    def __bool__(self):
        return self.type is not None
    
    def __str__(self):
        if self.type.type is None:
            return ""
        return self.type
    
    def promote(self):
        self.type = "q"
        self.value = piece_values[self.type]

class Move:
    def __init__(self, start, end):
        self.start = start # (file, rank)
        self.end = end # (file, rank)

    def __repr__(self):
        return f"{self.start}->{self.end}"
    
    def __str__(self):
        return f"{self.start}->{self.end}"

class Board:
    def __init__(self, fen=STARTING_FEN):
        self.parse_fen(fen)
        self.undo_list = [fen] # list of board states (fen) to undo moves
    
    def parse_fen(self, fen):
        # example: "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
        self.board = []
        fen_data = fen.split(" ") # 
        piece_placements = fen_data[0]
        active_color = fen_data[1]
        castling_availability = fen_data[2]
        en_passant_target = fen_data[3]
        halfmove_clock = fen_data[4]
        fullmove_number = fen_data[5]

        # parse the piece placements part of the fen
        for rank_num, rank in enumerate(piece_placements.split("/")):
            self.board.append([])
            file_num = 0
            for char in rank:
                if char.isdigit():
                    for _ in range(int(char)):
                        self.board[rank_num].append(Piece(None, (file_num, rank_num)))
                        file_num += 1
                else:
                    self.board[rank_num].append(Piece(char, (file_num, rank_num)))
                    file_num += 1

        # transpose the board to be [file][rank] instead of [rank][file]
        self.board = list(map(list, zip(*self.board)))
                
        
        self.white_to_move = active_color == "w"

        self.castling_availability = castling_availability

        # if en passant target is "-", then it.type is None
        if en_passant_target == "-":
            self.en_passant_target = None
        else:
            # convert the algebraic notation to a tuple
            en_passant_file = ord(en_passant_target[0]) - ord("a")
            en_passant_rank = 8 - int(en_passant_target[1])
            self.en_passant_target = (en_passant_file, en_passant_rank)

        self.halfmove_clock = int(halfmove_clock)
        self.fullmove_number = int(fullmove_number)

    def generate_fen(self):
        fen = ""
        # board is [file][rank] instead of [rank][file] so we need to transpose it
        for rank in list(map(list, zip(*self.board))):
            empty = 0
            for piece in rank:
                if piece.type is None:
                    empty += 1
                else:
                    if empty > 0:
                        fen += str(empty)
                        empty = 0
                    fen += piece.type
            if empty > 0:
                fen += str(empty)
            fen += "/"
        fen = fen[:-1] # remove the last "/"

        fen += " "
        fen += "w" if self.white_to_move else "b"

        fen += " "
        fen += self.castling_availability

        fen += " "
        fen += "-" if self.en_passant_target is None else chr(self.en_passant_target[0] + ord("a")) + str(8 - self.en_passant_target[1])

        fen += " "
        fen += str(self.halfmove_clock)

        fen += " "
        fen += str(self.fullmove_number)

        return fen

    def get_piece(self, position):
        file, rank = position
        return self.board[file][rank]
    
    def make_move(self, move):
        start = move.start # (file, rank)
        end = move.end # (file, rank)
        piece = self.get_piece(start)

        capture = False
        
        # if the piece is a pawn
        if piece.type == "p":
            # check if the move is a promotion
            if end[1] == 0 or end[1] == 7:
                piece.promote()

            # check if the move is an en passant
            if self.en_passant_target is not None and end == self.en_passant_target:
                # remove the pawn that was captured
                self.board[start[0]][end[1]] = Piece(None, (start[0], end[1]))
                capture = True

        # remove the en passant target
        self.en_passant_target = None
        if piece.type == "p":
            # check if the move is a double pawn push
            if abs(start[1] - end[1]) == 2:
                self.en_passant_target = (start[0], (start[1] + end[1]) // 2)

        
        # if the piece is a king
        if piece.type == "k":
            # update the castling availability
            if self.white_to_move:
                self.castling_availability = self.castling_availability.replace("K", "")
                self.castling_availability = self.castling_availability.replace("Q", "")
            else:
                self.castling_availability = self.castling_availability.replace("k", "")
                self.castling_availability = self.castling_availability.replace("q", "")

            # check if the move is a castling move
            if abs(start[0] - end[0]) == 2:
                # if the king is castling kingside
                if end[0] == 6:
                    # move the rook
                    self.board[7][end[1]] = Piece(None, (5, end[1]))
                # if the king is castling queenside
                elif end[0] == 2:
                    # move the rook
                    self.board[0][end[1]] = Piece(None, (3, end[1]))

        # if the piece is a rook
        if piece.type == "r":
            # update the castling availability
            if start == (0, 0):
                self.castling_availability = self.castling_availability.replace("Q", "") # white queenside
            elif start == (7, 0):
                self.castling_availability = self.castling_availability.replace("K", "") # white kingside
            elif start == (0, 7):
                self.castling_availability = self.castling_availability.replace("q", "") # black queenside
            elif start == (7, 7):
                self.castling_availability = self.castling_availability.replace("k", "") # black kingside

        # check if the move is a capture
        if self.get_piece(end).type is not None:
            capture = True

        # move the piece
        self.board[end[0]][end[1]] = piece
        self.board[start[0]][start[1]] = Piece(None, start)

        # update the turn
        self.white_to_move = not self.white_to_move

        # update the halfmove clock
        if piece.type == "p" or capture:
            self.halfmove_clock = 0
        else:
            self.halfmove_clock += 1

        # update the fullmove number
        if not self.white_to_move:
            self.fullmove_number += 1

        # add the board state to the undo list
        self.undo_list.append(self.generate_fen())

    def undo_move(self):
        if len(self.undo_list) > 1:
            self.parse_fen(self.undo_list.pop())

    def generate_pawn_moves(self, piece: Piece):
        file, rank = piece.position
        moves = []

        direction = 1 if piece.is_white else -1

        # check if the pawn can move forward one square
        if self.get_piece((file, rank + direction)).type is None:
            moves.append(Move(piece.position, (file, rank + direction)))

            # check if the pawn can move forward two squares
            if (rank == 1 and piece.is_white) or (rank == 6 and not piece.is_white):
                if self.get_piece((file, rank + 2 * direction)).type is None:
                    moves.append(Move(piece.position, (file, rank + 2 * direction)))

        # check if the pawn can capture a piece
        for i in [-1, 1]:
            if 0 <= file + i <= 7:
                target = self.get_piece((file + i, rank + direction))
                # if there is a piece to capture and it is an enemy piece
                if target and target.is_white != piece.is_white:
                    moves.append(Move(piece.position, (file + i, rank + direction)))
                    
        # check if the pawn can capture en passant
        if self.en_passant_target is not None:
            if self.en_passant_target == (file - 1, rank + direction) or self.en_passant_target == (file + 1, rank + direction):
                moves.append(Move(piece.position, self.en_passant_target))

        return moves
    
    def generate_rook_moves(self, piece: Piece):
        file, rank = piece.position
        moves = []
        
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        for direction in directions:
            # check if the rook can move in the direction until it hits a piece or the edge of the board
            for i in range(1, 8):
                # check if the move is on the board
                if 0 > file + i * direction[0] or file + i * direction[0] > 7 or 0 > rank + i * direction[1] or rank + i * direction[1] > 7:
                    break

                # get the piece at the target square
                target = self.get_piece((file + i * direction[0], rank + i * direction[1]))

                # if the target square is empty, add the move
                if target.type is None:
                    moves.append(Move(piece.position, (file + i * direction[0], rank + i * direction[1])))

                # if the target square is not empty, add the move if it is an enemy piece and break
                else:
                    if target.is_white != piece.is_white:
                        moves.append(Move(piece.position, (file + i * direction[0], rank + i * direction[1])))
                    break

        return moves
    
    def generate_bishop_moves(self, piece: Piece):
        file, rank = piece.position
        moves = []

        directions = [(1, 1), (-1, 1), (1, -1), (-1, -1)]
        for direction in directions:
            # check if the bishop can move in the direction until it hits a piece or the edge of the board
            for i in range(1, 8):
                # check if the move is on the board
                if 0 > file + i * direction[0] or file + i * direction[0] > 7 or 0 > rank + i * direction[1] or rank + i * direction[1] > 7:
                    break

                # get the piece at the target square
                target = self.get_piece((file + i * direction[0], rank + i * direction[1]))

                # if the target square is empty, add the move
                if target.type is None:
                    moves.append(Move(piece.position, (file + i * direction[0], rank + i * direction[1])))

                # if the target square is not empty, add the move if it is an enemy piece and break
                else:
                    if target.is_white != piece.is_white:
                        moves.append(Move(piece.position, (file + i * direction[0], rank + i * direction[1])))
                    break

        return moves

    def generate_knight_moves(self, piece: Piece):
        file, rank = piece.position
        moves = []

        directions = [(1, 2), # top right
                      (2, 1), # right top

                      (2, -1), # right bottom
                      (1, -2), # bottom right

                      (-1, -2), # bottom left
                      (-2, -1), # left bottom

                      (-2, 1), # left top
                      (-1, 2)] # top left

        for direction in directions:
            # check if the move is on the board
            if 0 > file + direction[0] or file + direction[0] > 7 or 0 > rank + direction[1] or rank + direction[1] > 7:
                continue

            # get the piece at the target square
            target = self.get_piece((file + direction[0], rank + direction[1]))

            # if the target square is empty, add the move
            if target.type is None:
                moves.append(Move(piece.position, (file + direction[0], rank + direction[1])))

            # if the target square is not empty, add the move if it is an enemy piece
            else:
                if target.is_white != piece.is_white:
                    moves.append(Move(piece.position, (file + direction[0], rank + direction[1])))

        return moves
    
    def generate_queen_moves(self, piece: Piece):
        # the queen moves are the combination of the rook and bishop moves
        return self.generate_rook_moves(piece) + self.generate_bishop_moves(piece)
    
    def generate_king_moves(self, piece: Piece):
        file, rank = piece.position
        moves = []

        # moving the king one square in any direction
        directions = [(1, 1), (-1, 1), (1, -1), (-1, -1), (1, 0), (-1, 0), (0, 1), (0, -1)]
        for direction in directions:
            # check if the move is on the board
            if 0 > file + direction[0] or file + direction[0] > 7 or 0 > rank + direction[1] or rank + direction[1] > 7:
                continue

            # get the piece at the target square
            target = self.get_piece((file + direction[0], rank + direction[1]))

            # if the target square is empty, add the move
            if target.type is None:
                moves.append(Move(piece.position, (file + direction[0], rank + direction[1])))

            # if the target square is not empty, add the move if it is an enemy piece
            else:
                if target.is_white != piece.is_white:
                    moves.append(Move(piece.position, (file + direction[0], rank + direction[1])))

        # castling moves
        if piece.is_white:
            if "K" in self.castling_availability:
                if self.get_piece((5, 0)).type is None and self.get_piece((6, 0)).type is None:
                    moves.append(Move(piece.position, (6, 0)))
            if "Q" in self.castling_availability:
                if self.get_piece((1, 0)).type is None and self.get_piece((2, 0)).type is None and self.get_piece((3, 0)).type is None:
                    moves.append(Move(piece.position, (2, 0)))
        else:
            if "k" in self.castling_availability:
                if self.get_piece((5, 7)).type is None and self.get_piece((6, 7)).type is None:
                    moves.append(Move(piece.position, (6, 7)))
            if "q" in self.castling_availability:
                if self.get_piece((1, 7)).type is None and self.get_piece((2, 7)).type is None and self.get_piece((3, 7)).type is None:
                    moves.append(Move(piece.position, (2, 7)))

        return moves
    
    def generate_moves(self, turn):
        moves = []
        for rank in self.board:
            for piece in rank:
                if piece.is_white == turn:
                    if piece.type == "p":
                        moves += self.generate_pawn_moves(piece)
                    elif piece.type == "r":
                        moves += self.generate_rook_moves(piece)
                    elif piece.type == "n":
                        moves += self.generate_knight_moves(piece)
                    elif piece.type == "b":
                        moves += self.generate_bishop_moves(piece)
                    elif piece.type == "q":
                        moves += self.generate_queen_moves(piece)
                    elif piece.type == "k":
                        moves += self.generate_king_moves(piece)

        return moves
    
    def is_en_passant_move(self, move):
        start = move.start
        end = move.end
        piece = self.get_piece(start)

        # if the piece is not a pawn, return False
        if piece.type != "p":
            return False
        # if end is the en passant target square
        if self.en_passant_target is not None and end == self.en_passant_target:
            return True
        return False

    def is_check(self, turn):
        '''
        Check if the king of the player with the turn is in check
        turn is the player to check if they are in check
        '''
        # generate all the moves of the opponent
        moves = self.generate_moves(not turn)
        for move in moves:
            # check if the move is a capture of the king
            piece = self.get_piece(move.end)
            if piece.type == "k" and piece.is_white == turn:
                return True
        return False

    def generate_legal_moves(self):
        moves = self.generate_moves(self.white_to_move)
        legal_moves = []
        for move in moves:
            self.make_move(move)
            if not self.is_check(self.white_to_move):
                legal_moves.append(move)
            self.undo_move()

        return legal_moves
    
    def is_checkmate(self):
        return len(self.generate_legal_moves()) == 0
    
    def is_stalemate(self):
        return len(self.generate_legal_moves()) == 0 and not self.is_check(self.white_to_move)
    
    def is_insufficient_material(self):
        # check if there are only kings left
        pieces = []
        for rank in self.board:
            for piece in rank:
                if piece.type is not None:
                    pieces.append(piece.type)
        if len(pieces) == 2:
            return True

        # check if there are only kings and one knight or one bishop left
        if len(pieces) == 3:
            if pieces.count("n") == 1 or pieces.count("b") == 1:
                return True

        return False

    def is_draw(self):
        return self.is_stalemate() or self.is_insufficient_material() or self.halfmove_clock >= 50
    
    def is_game_over(self):
        return self.is_checkmate() or self.is_draw()