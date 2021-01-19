import pygame

class Cell(object):
    def __init__(self, cell_type, pos, transparent, suit=None, col=None):
        super(Cell, self).__init__()
        self.cell_type = cell_type
        self.col = col
        self.dims = (58, 34)
        self.pos = pos
        self.suit = suit
        self.surf = pygame.Surface(self.dims)
        self.value = 0
        if cell_type == 'base':
            self.x = pos
            self.y = 16
        else:
            self.x = 16 if cell_type == 'cell' else 566
            self.y = 44 + pos * (self.dims[1] + 4)

        self.rect = self.surf.get_rect(topleft=(self.x, self.y))

        if cell_type == 'cell':
            self.surf.blit(pygame.image.load('empty_cell.bmp'), (0, 0))
            self.surf.set_colorkey(transparent)
        elif cell_type == 'foundation':
            suit = pygame.Surface((18, 18))
            self.surf.blit(pygame.image.load('foundation.bmp'), (0, 0))
            self.surf.set_colorkey(transparent)
            suit.blit(pygame.image.load('suits_large.bmp'), (-18 * pos, 0))
            suit.set_colorkey(transparent)
            if pos == 0:
                self.surf.blit(suit, ((self.dims[0] - 18) / 2, (self.dims[1] - 18) / 2 - 1))
            else:
                self.surf.blit(suit, ((self.dims[0] - 18) / 2, (self.dims[1] - 18) / 2 - 2))
        else:
            self.surf.blit(pygame.image.load('cascade_base.bmp'), (0, 0))
            self.surf.set_colorkey(transparent)
