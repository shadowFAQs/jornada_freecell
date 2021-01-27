import math
import pygame
from card import Card
from cell import Cell
from board import Board
from controller import Controller

def close_menu():
    print('Menu closed')

def is_tableau(stack):
    for i in range(1, len(stack)):
        card = stack[i]
        parent = stack[i - 1]
        if not card.value == parent.value - 1:
            return False
        if card.color == parent.color:
            return False
    return True

def is_valid_move(card, target, cards, cells, foundations, bases):
    if target in foundations:
        if card.value == target.value + 1 and card.suit == target.suit:
            if card.tableau:
                print('Invalid move of tableau to foundation')
                return False
            # Valid move to foundation
            return True
        else:
            print('Invalid move to empty foundation')
            return False
    if target in cells:
        if card.tableau:
            print('Invalid move of tableau to cell')
            return False
        # Valid move to free cell
        return True
    if target in bases:
        if card.tableau:
            if len(card.tableau) + 1 > get_max_draggable_tableau(cards, to_base=1):
                print('Invalid move of tableau to cascade base (too many cards in tableau)')
                return False
            else:
                print('Valid move to cascade base')
                return True
        else:
            print('Valid move to cascade base')
            return True
    if target.on_cell:
        print('Invalid move to card on cell')
        return False
    if target.on_foundation:
        if card.tableau:
            print('Invalid move of tableau to card on foundation')
            return False
        # Set target to highest value card on foundation
        foundation_target = sorted([c for c in cards if c.on_foundation and c.suit == target.suit], key=lambda c: c.value, reverse=True)[0]
        if card.value == foundation_target.value + 1 and card.suit == foundation_target.suit:
            # Valid move to card on foundation
            return True
        else:
            print(f'Invalid move to card on foundation: card {card.label} has value "{card.value}", suit "{card.suit}"; target {foundation_target.label} has value "{foundation_target.value}", suit "{foundation_target.suit}"')
            return False
    # Own column
    if card.col == target.col:
        print('Invalid move to own cascade')
        return False
    # Target not bottom card
    col_card = [c for c in cards if c.col == target.col][-1]
    if not target == col_card:
        print('Invalid move to card not at the bottom of its cascade')
        return False
    # Same-color card
    if col_card.color == card.color:
        print('Invalid move to card of same color')
        return False
    # Valid move
    if col_card.value == card.value + 1:
        return True
    else:
        # Not 1 higher
        print('Invalid move to card that is not 1 higher')
        return False

def open_menu():
    print('Menu open')

def toggle_menu():
    global MENU_OPEN
    if MENU_OPEN:
        MENU_OPEN = False
        close_menu()
    else:
        MENU_OPEN = True
        open_menu()

def win():
    global GAME_IN_PROGRESS
    GAME_IN_PROGRESS = False
    print('You win!')

def main():
    screen_dims = (240, 160)
    pygame.init()
    pygame.display.set_caption('GBA Freecell')
    screen = pygame.display.set_mode(screen_dims)

    controller = Controller() # Input device

    clock = pygame.time.Clock()
    fps = 0
    deal_event = pygame.USEREVENT + 0

    c_transparent = pygame.Color('#ff00ff')

    background = pygame.Surface(screen_dims)
    board_bmp = pygame.image.load('board.bmp')
    background.blit(board_bmp, (0, 0))

    global INPUT_ENABLED
    global GAME_IN_PROGRESS
    global MENU_OPEN
    global DEALING
    INPUT_ENABLED = False
    GAME_IN_PROGRESS = True
    DEALING = True
    MENU_OPEN = False

    # Card dims: 19 x 28
    deck_pos = (screen_dims[0] / 2 - 10, screen_dims[1] - 28 - 6)
    card_back = pygame.image.load('card_back.bmp')
    card_back.set_colorkey(c_transparent)

    suits = ('spades', 'clubs', 'diamonds', 'hearts')
    cells = [Cell(cell_type='cell', pos=n, col=0) for n in range(4)]
    foundations = [Cell(cell_type='foundation', pos=n, col=9, suit=suits[n]) for n in range(4)]
    bases = [Cell(cell_type='base', pos=n, col=1+n) for x in range(8)]

    cards = []
    for val in range(1, 14):
        for suit in suits:
            cards.append(
                Card(pos=deck_pos, transparent=c_transparent, value=val, suit=suit, suits=suits))

    board = Board(cards, foundations, cells, bases)
    board.shuffle()
    board.initialize_card_cols()
    board.initialize_card_target_positions()
    board.deal(deal_event)
    board.reset_tableaux()

    is_running = True

    while is_running:
        clock.tick(60)
        fps = clock.get_fps()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False

            elif event.type == deal_event:
                board.deal(deal_event)

            elif event.type == pygame.KEYDOWN:
                input_event = None
                if INPUT_ENABLED:
                    input_event = get_input_event(event, controller)

                if input_event == 'A press':
                    if board.selected_card:
                        # Should always be over a valid move
                        board.place_selected_card()
                        board.set_cards_z_index()
                    else:
                        # Should always be over a valid card to move
                        board.select_hovered()

                elif input_event == 'B press':
                    if board.selected_card:
                        board.deselect()

                elif input_event == 'D-PAD UP press':
                    board.handle_move_hover(direction='up')
                elif input_event == 'D-PAD RIGHT press':
                    board.handle_move_hover(direction='right')
                elif input_event == 'D-PAD DOWN press':
                    board.handle_move_hover(direction='down')
                elif input_event == 'D-PAD LEFT press':
                    board.handle_move_hover(direction='left')

                elif input_event == 'SPACE press':
                    toggle_menu()

        # Draw background (board)
        screen.blit(background, (0, 0))

        # Draw cards
        for card in board.cards:
            card.animate() # Update position if moving
            screen.blit(card.surf, card.pos)

        # Draw card back 'deck' while dealing
        if DEALING:
            screen.blit(card_back, deck_pos)

        # Wait for card animation
        INPUT_ENABLED = not bool(len([c for c in cards if c.animating]))

        pygame.display.update()

if __name__ == '__main__':
    main()

"""
TODO
----

- Menu
    - Show menu interface
    - Restart / new game
- Restack cards when cascades too long to fit on screen
- Update 'drop' placement of drag-and-drop so cursor doesn't need to be over target card
- Update 'click' so moving a couple pixels over the course of like 0.5s doesn't count as a drag
- Controller support
    1. Selection graphics
    2. Arrow / WASD input
    3. Map controller input
- Big refactor

"""
