import pygame

class Cell(object):
    def __init__(self, cell_type, pos, transparent):
        super(Cell, self).__init__()
        self.cell_type = cell_type
        self.dims = (58, 34)
        self.pos = pos
        self.surf = pygame.Surface(self.dims)
        self.x = 16 if cell_type == 'cell' else 566
        self.y = 44 + pos * (self.dims[1] + 4)

        if cell_type == 'cell':
            self.surf.blit(pygame.image.load('empty_cell.bmp'), (0, 0))
            self.surf.set_colorkey(transparent)
        else:
            suit = pygame.Surface((18, 18))
            self.surf.blit(pygame.image.load('foundation.bmp'), (0, 0))
            self.surf.set_colorkey(transparent)
            suit.blit(pygame.image.load('suits_large.bmp'), (-18 * pos, 0))
            suit.set_colorkey(transparent)
            if pos == 0:
                self.surf.blit(suit, ((self.dims[0] - 18) / 2, (self.dims[1] - 18) / 2 - 1))
            else:
                self.surf.blit(suit, ((self.dims[0] - 18) / 2, (self.dims[1] - 18) / 2 - 2))
