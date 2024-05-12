# pieces.py

piece_values = {
    'p': 1,
    'n': 3,
    'b': 3,
    'r': 5,
    'q': 9,
    'k': 1000

}

class Piece:
    def __init__(self, type):
        self.type = type
        self.team = 'white' if type.isupper() else 'black'
        self.value = piece_values[type.lower()]