import pygame

class Board(object):
    def __init__(self, cards, foundations, cells, bases):
        self.all_suits = cards[0].all_suits
        self.bases = bases
        self cards = cards
        self.cells = cells
        self.foundations = foundations
        self.hovered = None
        self.selected_card = None
        self.valid_moves = []

        self.hover_last_card_in_cascade(1)

    def activate_hovered(self):
        self.selected_card = self.hovered
        self.hovered = self.valid_moves[0]

    def count_empty_bases(self):
        return len([b for b in bases if b.vacant])

    def deselect(self):
        self.hovered = self.selected_card
        self.selected_card = None

    def find_first_card_with_valid_move(self, cards):
        for card in cards:
            # Card on cell
            if card.on_cell:
                # Can move to empty base
                if self.count_empty_bases():
                    return card
                # Can move to foundation
                foundation_card = self.get_top_card_on_foundation(suit=card.suit)
                if card.suit == foundation_card.suit and card.value == foundation_card.value + 1:
                    return card
                # Can move to bottom of cascade
                for bottom_card in [self.get_last_card_in_cascade(n) for n in range(1, 9)]:
                    if bottom_card.color != card.color and bottom_card.value == card.value + 1:
                        return card

            # Card on foundation
            elif card.on_foundation:
                # Can move to free cell or empty base
                if self.count_free_cells() or self.count_empty_bases():
                    return card
                # Can move to bottom of cascade
                for bottom_card in [self.get_last_card_in_cascade(n) for n in range(1, 9)]:
                    if bottom_card.color != card.color and bottom_card.value == card.value + 1:
                        return card

            # Card at bottom of cascade
            elif card == self.get_last_card_in_cascade(index=card.col):
                # Can move to free cell or empty base
                if self.count_free_cells() or self.count_empty_bases():
                    return card
                # Can move to foundation
                foundation_card = self.get_top_card_on_foundation(suit=card.suit)
                if card.suit == foundation_card.suit and card.value == foundation_card.value + 1:
                    return card
                # Can move to bottom of another cascade
                for bottom_card in [self.get_last_card_in_cascade(n) for n in range(1, 9)]:
                    if bottom_card.color != card.color and bottom_card.value == card.value + 1:
                        return card

            # Card in cascade, but not at the bottom
            else:
                if len(card.tableau) <= self.get_max_tableau_size():
                    # Can move to empty base
                    if self.count_empty_bases():
                        return card
                    # Can move to bottom of another cascade
                    for bottom_card in [self.get_last_card_in_cascade(n) for n in range(1, 9)]:
                        if bottom_card.color != card.color and bottom_card.value == card.value + 1:
                            return card

        return None

    def get_available_cells(self):
        return [c for c in self.cells if c.vacant]

    def get_cards_on_cells(self):
        return [c for c in self.cards if c.on_cell]

    def get_empty_bases(self):
        return [b for b in self.bases if b.vacant]

    def get_cascade_offset_from_card(self, card):
        num_cards_in_col = len([c for c in self.cards if c.col == card.col])
        offset = 18 # TODO: Shrink offset if num_cards_in_col too high
        y_pos = card.pos[1] + offset
        return (card.pos[0], y_pos)

    def get_last_card_in_cascade(self, index):
        cascade = [c for c in cards if c.col == index]
        return sorted(cascade, key=lambda c:c.y)[-1] if cascade else None

    def get_max_tableau_size(self):
        return (5 - len([c for c in self.cards if c.on_cell])) * (self.count_empty_bases() + 1)

    def get_top_card_on_foundation(self, suit):
        cards = [c for c in self.cards if c.on_foundation and c.suit == suit]
        return sorted(cards, key=lambda c: c.value)[-1]

    def handle_move_hover(self, direction):
        """
        Different logic is used to determine where to move the hover
        selector, depending on whether or not there is already a card
        selected. This function makes that switch.
        """
        if self.selected_card:
            self.move_hover_with_selection(direction)
        else:
            self.move_hover_with_no_selection(direction)

    def move_hover_with_no_selection(self, direction):
        """
        Determines whether the hover selector can be moved to a valid
        card in a given direction. If so, the selector is moved to the
        nearest valid card in that direction; if not, no move is made.

        This fn is called when there is no card selected already.
        """
        if direction == 'up':
            # Check cards above in current column
            cards_to_check = [c for c in self.cards if c.col == self.hovered.col and c.y < self.hovered.y]
            cards_to_check = sorted(cards_to_check, key=lambda c: c.y, reverse=True)

        elif direction == 'right':
            # Check cards in cascades to the right
            cards_to_check = [c for c in self.cards if c.col > self.hovered.col]
            # Check cards on foundations
            if hovered.col < 9:
                cards_to_check += [get_top_card_on_foundation(suit) for suit in self.all_suits]
            cards_to_check = sorted(cards_to_check, key=lambda c: c.x)

        elif direction == 'down':
            # Check cards below in current column
            cards_to_check = [c for c in self.cards if c.col == self.hovered.col and c.y < self.hovered.y]
            cards_to_check = sorted(cards_to_check, key=lambda c: c.y)

        elif direction == 'left':
            # Check cards in cascades to the left
            cards_to_check = [c for c in self.cards if c.col < self.hovered.col]
            # Check cards on cells
            if hovered.col > 0:
                cards_to_check += get_cards_on_cells()
            cards_to_check = sorted(cards_to_check, key=lambda c: c.x, reverse=True)

        if cards_to_check:
            hover = self.find_first_card_with_valid_move(cards_to_check)
            if hover:
                self.hovered = hover

    def move_hover_with_selection(self, direction):
        """
        Determines whether the hover selector can be moved to a valid
        place in a given direction. If so, the selector is moved to the
        nearest valid place in that direction; if not, no move is made.

        This fn is called when there is already a card selected.
        """
        pass # TODO: Pick it up here

    def place_selected_card(self):
        self.selected_card.on_cell = False
        self.selected_card.on_foundation = False

        # On free cell
        if self.hovered in cells:
            self.selected_card.on_cell = True
            self.selected_card.move(pos=self.hovered.pos, col=0)
            self.hovered = self.selected_card

        # On foundation, or on card on foundation
        elif self.hovered.on_foundation or self.hovered in self.foundations:
            self.selected_card.on_foundation = True
            self.selected_card.move(pos=self.hovered.pos, col=9)
            self.select_top_foundation_card(suit=self.hovered.suit)

        # On empty base
        elif self.hovered in bases:
            self.selected_card.move(pos=self.hovered.pos, col=self.hovered.col)
            self.hovered = self.get_last_card_in_cascade(self.hovered.col)

        # On bottom of cascade
        else:
            self.selected_card.move(pos=self.get_cascade_offset_from_card(self.hovered), col=self.hovered.col)
            self.hovered = self.get_last_card_in_cascade(self.hovered.col)

        self.selected_card = None

    def select_top_foundation_card(self, suit):
        self.hovered = sorted([c for c in cards if c.suit == suit and c.on_foundation], key=lambda c: c.value)[-1]
