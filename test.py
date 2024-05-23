import timeit


class Move:
    def __init__(self, start, end, start_piece, captured_piece=0, promotion=0, castling=0, capture=0, en_passant=0):
        self.start = start
        self.end = end
        self.start_piece = start_piece
        self.captured_piece = captured_piece
        self.promotion = promotion
        self.castling = castling
        self.capture = capture
        self.en_passant = en_passant

def move_class():
    move1 = Move(0, 1, 1, 0, 0, 0, 0, 0)
    move2 = Move(6, 4, 5, 0, 3, 0, 2, 4)
    move3 = Move(1, 7, 1, 6, 4, 3, 1, 4)
    move4 = Move(3, 2, 2, 0, 0, 0, 0, 0)
    


def move_tuple():
    move1 = (0, 1, 1, 0, 0, 0, 0, 0)
    move2 = (6, 4, 5, 0, 3, 0, 2, 4)
    move3 = (1, 7, 1, 6, 4, 3, 1, 4)
    move4 = (3, 2, 2, 0, 0, 0, 0, 0)
    

move_class_time = timeit.timeit(move_class, number=100000)

tuple_time = timeit.timeit(move_tuple, number=100000)

print(f"Move class: {move_class_time} seconds")
print(f"Tuple: {tuple_time} seconds")