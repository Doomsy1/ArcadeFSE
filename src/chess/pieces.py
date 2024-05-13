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
    def __init__(self, type, position):
        if type is not None:
            self.type = type.lower()
            self.color = "black" if type.islower() else "white"
            self.value = piece_values[self.type]
            self.position = position
        else:
            self.type = None
            self.color = None
            self.value = 0
            self.position = position

    def __repr__(self):
        return self.type

    def __bool__(self):
        return self.type is not None
    
    def __str__(self):
        if self.type is None:
            return " "
        return self.type