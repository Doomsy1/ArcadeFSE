def switch_fen_colors(fen):
    # Define a translation table to switch piece colors
    trans_table = str.maketrans("rnbqkpRNBQKP", "RNBQKPrnbqkp")
    
    # Split the FEN string into its components
    board, active_color, castling, en_passant, halfmove_clock, fullmove_number = fen.split()
    
    # Translate the piece placements and reverse the order of the ranks
    ranks = board.split('/')
    new_ranks = [rank.translate(trans_table) for rank in ranks]
    new_board = '/'.join(new_ranks[::-1])
    
    # Switch the active color
    new_active_color = 'b' if active_color == 'w' else 'w'
    
    # Translate castling rights
    new_castling = castling.translate(trans_table)
    
    # Translate en passant target square (if it's not '-')
    new_en_passant = en_passant
    if en_passant != '-':
        new_en_passant = en_passant[0] + ('6' if en_passant[1] == '3' else '3' if en_passant[1] == '6' else en_passant[1])
    
    # The halfmove clock and fullmove number remain the same
    new_halfmove_clock = halfmove_clock
    new_fullmove_number = fullmove_number
    
    # Combine the components into the new FEN string
    new_fen = f"{new_board} {new_active_color} {new_castling} {new_en_passant} {new_halfmove_clock} {new_fullmove_number}"
    
    return new_fen

if __name__ == "__main__":
    fen = "2b3N1/8/1r2pN1b/1p2kp2/1P1R4/8/4K3/6Q1 w - - 0 1"
    

    print(f"Original FEN: {fen}")
    print(f"Switched FEN: {switch_fen_colors(fen)}")