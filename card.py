import math
import pygame

class Card(object):
    def __init__(self, pos, transparent, value, suit):
        super(Card, self).__init__()
        self.all_values = [0, 'A', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K']
        self.all_suits = ['spades', 'clubs', 'diamonds', 'hearts']
        self.animating = False
        self.c_transparent = transparent
        self.col = 0
        self.dims = (58, 34)
        self.face_up = False
        self.on_cell = False
        self.on_foundation = False
        self.pos = pos
        self.suit = suit
        self.surf = pygame.Surface(self.dims)
        self.surf_suit = pygame.Surface((16, 16))
        self.surf_value = pygame.Surface((16, 16))
        self.tableau = []
        self.target_pos = pos
        self.value = value

        self.color = 'black' if suit in ('spades', 'clubs') else 'red'
        self.set_label()

        # Graphics
        self.surf_suit.set_colorkey(self.c_transparent)
        self.surf_value.set_colorkey(self.c_transparent)
        self.bmp_back = pygame.image.load('card_back.bmp')
        self.bmp_front = pygame.image.load('card_front.bmp')
        self.bmp_suits = pygame.image.load('suits.bmp')
        self.bmp_values_black = pygame.image.load('values_black.bmp')
        self.bmp_values_red = pygame.image.load('values_red.bmp')
        self.draw_face()

    def draw_face(self):
        suit_index = self.all_suits.index(self.suit)
        self.surf.blit(self.bmp_front, (0, 0))
        if self.color == 'black':
            self.surf_value.blit(
                self.bmp_values_black, (-16 * (self.value - 1), 0))
        else:
            self.surf_value.blit(
                self.bmp_values_red, (-16 * (self.value - 1), 0))
        self.surf_suit.blit(self.bmp_suits, (-16 * suit_index, 0))
        self.surf.blit(self.surf_value, (8, 2))
        self.surf.blit(self.surf_suit, (26, 2))
        self.surf.set_colorkey(self.c_transparent)

    def move(self, pos):
        self.pos = pos
        self.target_pos = pos
        self.col = col

        self.move_tableau(col)

    def move_tableau(self, col=None):
        for i in range(len(self.tableau)):
            card = self.tableau[i]
            card.pos = (self.pos[0], self.pos[1] + 18 + i * 18)
            card.target_pos = card.pos

    def set_label(self):
        value = self.all_values[self.value]
        self.label = f"{value}{self.suit[0].upper()}"

    def update(self, mouse_pos=None):
        if self.animating:
            if not self.pos == self.target_pos:
                x_diff = self.target_pos[0] - self.pos[0]
                y_diff = self.target_pos[1] - self.pos[1]
                if x_diff > 0:
                    self.x += math.ceil(abs(x_diff / 5))
                elif x_diff < 0:
                    self.x -= math.ceil(abs(x_diff / 5))
                if y_diff > 0:
                    self.y += math.ceil(abs(y_diff / 5))
                elif y_diff < 0:
                    self.y -= math.ceil(abs(y_diff / 5))

                x_diff = self.target_pos[0] - self.pos[0]
                y_diff = self.target_pos[1] - self.pos[1]
                if abs(x_diff) < 2:
                    self.pos = (self.target_pos[0], self.pos[1])
                if abs(y_diff) < 2:
                    self.pos = (self.pos[0], self.target_pos[1])
            else:
                self.animating = False
