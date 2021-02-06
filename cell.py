import pygame

class Cell(object):
    def __init__(self, cell_type, pos, col, suit=None):
        self.cell_type = cell_type
        self.col = col
        self.dims = (19, 28)
        self.suit = suit
        self.vacant = True

        if cell_type == 'base':
            # Anchor point for base 0 is (32, 6)
            # Bases are 22px apart
            self.label = f'base (col {col})'
            self.pos = (32 + pos * 22, 6)
            self.vacant = False

        elif cell_type == 'cell':
            # Anchor point for cell 0 is (7, 6)
            # Cells are 40px apart
            self.card = None
            self.label = f'cell #{pos}'
            self.pos = (7, 6 + pos * 40)

        elif cell_type == 'foundation':
            # Anchor point for foundation 0 is (215, 6)
            # Foundations are 40px apart
            self.label = f'{suit} foundation'
            self.pos = (215, 6 + pos * 40)
