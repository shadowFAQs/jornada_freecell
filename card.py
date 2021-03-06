import math
import pygame
from logger import log

class Card(object):
    def __init__(self, pos, transparent, value, suit, suits):
        self.all_values = [0, 'A', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K']
        self.all_suits = suits
        self.animating = False
        self.c_transparent = transparent
        self.col = 0
        self.dims = (19, 28)
        self.face_up = False
        self.highlight = False
        self.on_cell = False
        self.on_foundation = False
        self.pos = pos
        self.suit = suit
        self.surf = pygame.Surface(self.dims)
        self.surf_suit = pygame.Surface((7, 8))
        self.surf_value = pygame.Surface((8, 8))
        self.tableau = []
        self.target_pos = pos
        self.value = value

        self.color = 'black' if suit in suits[:2] else 'red'
        self.set_label() # For debugging

        # Graphics
        self.surf_suit.set_colorkey(self.c_transparent)
        self.surf_value.set_colorkey(self.c_transparent)
        self.bmp_face_normal = pygame.image.load('card_face.bmp')
        self.bmp_face_highlight = pygame.image.load('card_face_highlight.bmp')
        self.bmp_suits = pygame.image.load('suits.bmp')
        self.bmp_values = pygame.image.load('values.bmp')
        self.draw_face(self.bmp_face_normal)

    def draw_face(self, front):
        suit_index = self.all_suits.index(self.suit)
        # Draw card front
        self.surf.blit(front, (0, 0))
        # Draw value (each value sprite is 8px wide)
        self.surf_value.blit(self.bmp_values, (-8 * (self.value - 1), 0))
        # Draw suit (each suit is 7px wide)
        self.surf_suit.blit(self.bmp_suits, (-7 * suit_index, 0))
        # Blit value and suit to main surface
        self.surf.blit(self.surf_value, (3, 3))
        self.surf.blit(self.surf_suit, (10, 3))
        self.surf.set_colorkey(self.c_transparent)

    def move(self, pos, col):
        self.pos = pos
        self.target_pos = pos
        self.col = col

        log('card.move', f'{self.label} moved to col {self.col} @ {self.pos}')

        self.move_tableau(col)

    def move_tableau(self, col):
        for i in range(len(self.tableau)):
            card = self.tableau[i]
            card.pos = (self.pos[0], self.pos[1] + 14 + i * 14)
            card.target_pos = card.pos
            card.col = col

            log('card.move_tableau', f'(Part of tableau) {card.label} moved to col {card.col} @ {card.pos}')

    def set_label(self):
        value = self.all_values[self.value]
        self.label = f"{value}{self.suit[0].upper()}"

    def update(self):
        # Update display position (during deal)
        if self.animating:
            if self.pos != self.target_pos:
                x_diff = self.target_pos[0] - self.pos[0]
                y_diff = self.target_pos[1] - self.pos[1]
                if x_diff > 0:
                    x = self.pos[0] + math.ceil(abs(x_diff / 5))
                    self.pos = (x, self.pos[1])
                elif x_diff < 0:
                    x = self.pos[0] - math.ceil(abs(x_diff / 5))
                    self.pos = (x, self.pos[1])
                if y_diff > 0:
                    y = self.pos[1] + math.ceil(abs(y_diff / 5))
                    self.pos = (self.pos[0], y)
                elif y_diff < 0:
                    y = self.pos[1] - math.ceil(abs(y_diff / 5))
                    self.pos = (self.pos[0], y)

                x_diff = self.target_pos[0] - self.pos[0]
                y_diff = self.target_pos[1] - self.pos[1]
                if abs(x_diff) < 2:
                    self.pos = (self.target_pos[0], self.pos[1])
                if abs(y_diff) < 2:
                    self.pos = (self.pos[0], self.target_pos[1])
            else:
                self.animating = False

        # Draw hovered / unhovered face
        if self.highlight:
            self.draw_face(self.bmp_face_highlight)
        else:
            self.draw_face(self.bmp_face_normal)
