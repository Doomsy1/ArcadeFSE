# pieces.py

import pygame

class Piece:
    def __init__(self, type):
        self.type = type
        self.team = 'white' if type.isupper() else 'black'

    def get_team(self):
        return self.team
    
    def get_type(self):
        return self.type