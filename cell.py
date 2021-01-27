import pygame

class Cell(object):
    def __init__(self, cell_type, pos, col, suit=None):
        self.cell_type = cell_type
        self.col = col
        self.suit = suit
        self.vacant = True

        if cell_type == 'base':
            # Anchor point for base 0 is (32, 6)
            # Bases are 23px apart
            self.pos = (32 + pos * 23, 6)
            self.vacant = False

        elif cell_type == 'cell':
            # Anchor point for cell 0 is (7, 6)
            # Cells are 40px apart
            self.pos = (16, 6 + pos * 40)
            self.card = None

        elif cell_type == 'foundation':
            # Anchor point for foundation 0 is (216, 6)
            # Foundations are 40px apart
            self.pos = (216, 6 + pos * 40)
