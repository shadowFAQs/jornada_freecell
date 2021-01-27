import random
import pygame

class Board(object):
    def __init__(self, cards, foundations, cells, bases):
        self.all_suits = cards[0].all_suits
        self.bases = bases
        self.cards = cards
        self.cells = cells
        self.foundations = foundations
        self.hovered = None
        self.selected_card = None
        self.valid_moves = []

    def activate_hovered(self):
        self.selected_card = self.hovered
        self.hovered = self.valid_moves[0]

    def count_empty_bases(self):
        return len([b for b in bases if b.vacant])

    def deal(self, deal_event):
        to_deal = [c for c in self.cards if not c.animating and c.pos != c.target_pos]
        if to_deal:
            card = to_deal[0]
            card.animating = True
            pygame.time.set_timer(deal_event, 50, True)

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

    def find_first_valid_position_for_selected_card(self, positions):
        for position in positions:
            # Empty foundation (Ace selected)
            if position in self.foundations:
                if self.selected_card.value == 1:
                    return position

            # Empty cell or base
            if position in self.cells or position in self.bases:
                return position

            # Same-suit card on foundation (suit check already done)
            if position.on_foundation and position.value == self.selected_card.value - 1:
                return position

            # Valid move to cascade
            if position.color != self.selected_card.color and position.value == self.selected_card.value + 1:
                return position

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
        return sorted(cascade, key=lambda c:c.pos[1])[-1] if cascade else None

    def get_max_tableau_size(self):
        return (5 - len([c for c in self.cards if c.on_cell])) * (self.count_empty_bases() + 1)

    def get_top_card_on_foundation(self, suit):
        cards = [c for c in self.cards if c.on_foundation and c.suit == suit]
        return sorted(cards, key=lambda c: c.value)[-1] if cards else None

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

    def hover_last_card_in_cascade(self, index):
        cards_in_cascade = [c for c in self.cards if c.col == index]
        self.hovered = sorted(cards_in_cascade, key=lambda c: c.pos[1])[-1]

    def initialize_card_cols(self):
        """
        col 0:    cells
        cols 1-8: cascades
        col 9:    foundations
        """
        col = 1
        for card in self.cards:
            if col > 9:
                col = 1
            card.col = col
            col += 1

    def initialize_card_target_positions(self):
        # Anchor point for card at top of col 0 is (32, 6)
        # Cascades are 23px apart
        # Cards in cascades are stacked 14px apart
        for n in range(1, 9):
            for i, card in enumerate([c for c in self.cards if c.col == n]):
                x_pos = 32 + (n - 1) * 22
                y_pos = 6 + i * 14
                card.target_pos = (x_pos, y_pos)

    def move_hover_with_no_selection(self, direction):
        """
        Determines whether the hover selector can be moved to a valid
        card in a given direction. If so, the selector is moved to the
        nearest valid card in that direction; if not, no move is made.

        This fn is called when there is no card selected already.
        """
        if direction == 'up':
            # Check cards above in current column
            positions_to_check = [c for c in self.cards if c.col == self.hovered.col and c.pos[1] < self.hovered.pos[1]]
            positions_to_check = sorted(positions_to_check, key=lambda c: c.pos[1], reverse=True)

        elif direction == 'right':
            # Check cards in cascades to the right
            positions_to_check = [c for c in self.cards if c.col > self.hovered.col]
            # Check cards on foundations
            if hovered.col < 9:
                for suit in suits:
                    foundation_card = get_top_card_on_foundation(suit)
                    if foundation_card:
                        positions_to_check.append(foundation_card)
            positions_to_check = sorted(positions_to_check, key=lambda c: c.x)

        elif direction == 'down':
            # Check cards below in current column
            positions_to_check = [c for c in self.cards if c.col == self.hovered.col and c.pos[1] < self.hovered.pos[1]]
            positions_to_check = sorted(positions_to_check, key=lambda c: c.pos[1])

        elif direction == 'left':
            # Check cards in cascades to the left
            positions_to_check = [c for c in self.cards if c.col < self.hovered.col]
            # Check cards on cells
            if hovered.col > 0:
                positions_to_check += get_cards_on_cells()
            positions_to_check = sorted(positions_to_check, key=lambda c: c.x, reverse=True)

        if positions_to_check:
            hover = self.find_first_card_with_valid_move(positions_to_check)
            if hover:
                self.hovered = hover

    def move_hover_with_selection(self, direction):
        """
        Determines whether the hover selector can be moved to a valid
        place in a given direction. If so, the selector is moved to the
        nearest valid place in that direction; if not, no move is made.

        This fn is called when there is already a card selected.

        ('Up' and 'Down' are not considered here, as there is no case
        where a player can move a card to a higher or lower position
        within a cascade, or from one foundation to another, and moving between cells is not allowed in this version because it is
        pointless.)
        """
        if direction == 'right':
            # Check bottom cards in cascades to the right
            positions_to_check = [self.get_last_card_in_cascade(n) for n in range(self.hovered.col, 9)]
            # Check card on same-suit foundation
            if hovered.col < 9:
                foundation_card = get_top_card_on_foundation(selected_card.suit)
                if foundation_card:
                    positions_to_check.append(foundation_card)
                else:
                    # Check empty foundation (if moving an Ace)
                    if self.selected_card.value == 1:
                        positions_to_check.append([f for f in self.foundations if f.suit == self.selected_card.suit])
            # Check empty bases
            positions_to_check += [b for b in self.bases if b.vacant and b.col > self.hovered.col]

            # Sort positions by column from low to high
            positions_to_check = sorted(positions_to_check, key=lambda p: p.col)
        elif direction == 'left':
            # Check bottom cards in cascades to the left
            positions_to_check = [self.get_last_card_in_cascade(n) for n in range(1, self.hovered.col)]
            # Check empty cells
            positions_to_check += [c for c in self.cells if c.vacant]
            # Check empty bases
            positions_to_check += [b for b in self.bases if b.vacant and b.col < self.hovered.col]

            # Sort positions by column from high to low
            positions_to_check = sorted(positions_to_check, key=lambda p: p.col, reverse=True)

        if positions_to_check:
            hover = self.find_first_valid_position_for_selected_card(positions_to_check)
            if hover:
                self.hovered = hover

    def place_selected_card(self):
        """
        Move selected card to 'hovered' position. This position is
        assumed to be a valid move.
        """
        if selected_card.on_cell:
            # Clear 'card' prop from cell that selected_card moved from
            cell = [c for c in self.cells if c.card == self.selected_card]
            cell.card = None
            cell.vacant = True

        self.selected_card.on_cell = False
        self.selected_card.on_foundation = False

        # On free cell
        if self.hovered in cells:
            self.selected_card.on_cell = True
            self.selected_card.move(pos=self.hovered.pos, col=0)
            self.hovered.card = self.selected_card
            self.hovered.vacant = False
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

    def reset_tableaux(self):
        for card in self.cards:
            card.tableau = []
            cards_below = [c for c in self.cards if c.col == card.col and c.target_pos[1] > card.target_pos[1] and not c.on_foundation and not c.on_cell]
            for n in range(len(cards_below)):
                child = cards_below[n]
                parent = cards_below[n - 1] if n else card
                if child.value == parent.value - 1 and not child.color == parent.color:
                    card.tableau.append(child)
                else:
                    break

    def select_top_foundation_card(self, suit):
        self.hovered = sorted([c for c in cards if c.suit == suit and c.on_foundation], key=lambda c: c.value)[-1]

    def set_cards_z_index(self):
        """
        Card draw order:
        1. Cards in cascades (by Y value, low to high)
        2. Cards on foundations (by value, low to high)
        3. Cards on cells (unsorted)
        """
        cascade_cards = sorted([c for c in self.cards if not c.on_cell and not c.on_foundation], key=lambda c: c.pos[1])
        foundation_cards = sorted([c for c in self.cards if c.on_foundation], key=lambda c: c.value)
        self.cards = cascade_cards + foundation_cards + [c for c in self.cards if c.on_cell]

    def shuffle(self):
        random.shuffle(self.cards)
