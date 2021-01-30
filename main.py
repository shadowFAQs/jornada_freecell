import pygame
import logger
from card import Card
from cell import Cell
from board import Board
from controller import Controller

def close_menu():
    print('Menu closed')

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
    logger.init_log()

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
    bases = [Cell(cell_type='base', pos=n, col=n+1) for n in range(8)]

    cards = []
    for val in range(1, 14):
        for suit in suits:
            cards.append(
                Card(pos=deck_pos, transparent=c_transparent, value=val, suit=suit, suits=suits))

    board = Board(cards, foundations, cells, bases, c_transparent)
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

            elif event.type in (pygame.KEYDOWN, pygame.KEYUP):
                input_event = None
                if INPUT_ENABLED:
                    input_event = controller.get_action_button(event)

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
            if not DEALING:
                board.update_highlights()
            card.update()
            screen.blit(card.surf, card.pos)

        # Draw hover markers, if applicable
        if board.selected_card:
            for n in range(len(board.hover_markers)):
                screen.blit(board.hover_markers[n], (board.hover_marker_positions[n]))

        # Draw card back 'deck' while dealing
        if DEALING:
            if [c for c in board.cards if c.pos != c.target_pos and not c.animating]:
                screen.blit(card_back, deck_pos)
            # Unset DEALING flag when cards are done animating
            cards_animating = [c for c in board.cards if c.animating]
            if not cards_animating:
                DEALING = False
                INPUT_ENABLED = True
                # Select bottom card in first cascade
                board.hover_last_card_in_cascade(1)

        pygame.display.update()

if __name__ == '__main__':
    main()

"""
TODO
----

- Bug: Can move tableau to cell
- Wrap L/R hover moves around screen
- After moving a card to a foundation, set hover back to the last card in the column the card came from (if it has a move; if not, the next closest one)
- Hold DPAD buttons to repeat 'press' event after delay
- Create & implement graphics for hovered cells
- Create & implement graphics for hovered foundations
- Create & implement graphics for hovered bases
- Update board.get_cascade_offset_from_card() when cascades get too long
- Menu
    - Show menu interface
    - Solve
    - New game
    - Statistics
- Controller support
    1. Selection graphics
    2. Arrow / WASD input
    3. Map controller input

"""
