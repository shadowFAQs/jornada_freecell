import math
import pygame

class Card(object):
    def __init__(self, transparent, value, suit):
        super(Card, self).__init__()
        self.animating = False
        self.c_transparent = transparent
        self.col = 0
        self.dims = (58, 34)
        self.drag_offset = (0, 0)
        self.dragging = False
        self.face_up = False
        self.on_cell = False
        self.on_foundation = False
        self.pile_pos = 0
        self.rect = None
        self.suit = suit
        self.surf = pygame.Surface(self.dims)
        self.surf_suit = pygame.Surface((16, 16))
        self.surf_value = pygame.Surface((16, 16))
        self.tableau = []
        self.target_x = 290
        self.target_y = 250
        self.value = value
        self.x = 290 # Left of card
        self.y = 250 # Top of card

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
        suit_index = ['spades', 'clubs', 'diamonds', 'hearts'].index(self.suit)
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

    def move(self, pos, col=None):
        self.x = pos[0]
        self.y = pos[1]
        self.target_x = self.x
        self.target_y = self.y
        self.rect = self.surf.get_rect(topleft=(self.target_x, self.target_y))
        if not col == None: # Differentiate between 0 and None
            self.col = col
            print(f'{self.label}: col={self.col}')
        self.move_tableau(col)

    def move_tableau(self, col=None):
        for i in range(len(self.tableau)):
            card = self.tableau[i]
            card.x = self.x
            card.y = self.y + 18 + i * 18
            card.target_x = card.x
            card.target_y = card.y
            card.rect = card.surf.get_rect(topleft=(card.target_x, card.target_y))

            if not col == None: # Differentiate between 0 and None
                card.col = col
                print(f'{card.label}: col={card.col}')

    def set_label(self):
        value = [0, 'A', 2, 3, 4, 5, 6, 7, 8, 9, 10, 'J', 'Q', 'K'][self.value]
        self.label = f"{value}{self.suit[0].upper()}"

    def update(self, mouse_pos=None):
        if self.animating:
            if not (self.x, self.y) == (self.target_x, self.target_y):
                x_diff = self.target_x - self.x
                y_diff = self.target_y - self.y
                if x_diff > 0:
                    self.x += math.ceil(abs(x_diff / 5))
                elif x_diff < 0:
                    self.x -= math.ceil(abs(x_diff / 5))
                if y_diff > 0:
                    self.y += math.ceil(abs(y_diff / 5))
                elif y_diff < 0:
                    self.y -= math.ceil(abs(y_diff / 5))

                x_diff = self.target_x - self.x
                y_diff = self.target_y - self.y
                if abs(x_diff) < 2:
                    self.x = self.target_x
                if abs(y_diff) < 2:
                    self.y = self.target_y
            else:
                self.animating = False
        elif self.dragging:
            self.x = mouse_pos[0] - self.drag_offset[0]
            self.y = mouse_pos[1] - self.drag_offset[1]
            self.move_tableau()
