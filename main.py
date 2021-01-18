import math, random
import pygame
from card import Card
from cell import Cell

def deal(deck, deal_event):
    card = [c for c in deck if not c.animating and not (c.x, c.y) == (c.target_x, c.target_y)]
    if card:
        card = card[0]
        card.animating = True
        pygame.time.set_timer(deal_event, 50, True)

def get_cascade_pos(cards, col):
    bottom_card = [c for c in cards if c.col == col][-1]
    return (bottom_card.x, bottom_card.y + 18)

def get_selected_card(event, cards):
    cards_under_cursor = [c for c in cards if c.rect.collidepoint(event.pos)]
    cards_under_cursor = sorted(cards_under_cursor, key=lambda c: c.y, reverse=True)
    if cards_under_cursor:
        return cards_under_cursor[0]
    else:
        return None

def is_draggable(card, cards):
    # Bottom card in tableu
    if card == [c for c in cards if c.col == card.col][-1]:
        return True
    # Non-bottom card, but all below are in a tableu
    stack = [c for c in cards if c.col == card.col and c.y >= card.y]
    return bool(is_tableau(stack))

def is_tableau(stack):
    for i in range(1, len(stack)):
        card = stack[i]
        parent = stack[i - 1]
        if not card.value == parent.value - 1:
            return False
        if card.color == parent.color:
            return False
    return True

def is_valid_move(card, target, col, cards):
    # Own column
    if card.col == col:
        return False
    col_card = [c for c in cards if c.col == col][-1]
    # Target not bottom card
    if not target == col_card:
        return False
    # Same-color card
    if col_card.color == card.color:
        return False
    # Valid move
    if col_card.value == card.value + 1:
        return True
    else:
        # Not one higher
        return False

def reset_tableaux(cards):
    pass # TODO: update this after every move (and on initial deal)

def set_card_positions(deck, x_pos):
    col = 0
    row = 0
    for card in deck:
        if col > 7:
            col = 0
            row += 1
        card.col = col
        card.target_x = x_pos[col]
        card.target_y = 16 + row * 18
        card.rect = card.surf.get_rect(topleft=(card.target_x, card.target_y))
        col += 1

def set_z_indexes(cards):
    return sorted(cards, key=lambda c: c.y)

def main():
    dims = (640, 240)
    pygame.init()
    pygame.display.set_caption('Jornada Freecell')
    window_surface = pygame.display.set_mode(dims)

    clock = pygame.time.Clock()
    fps = 0
    deal_event = pygame.USEREVENT + 0

    c_background = pygame.Color('#cadc9f')
    c_transparent = pygame.Color('#ff00ff')

    background = pygame.Surface(dims)
    background.fill(c_background)
    board = pygame.Surface(dims)
    board_bmp = pygame.image.load('board.bmp')
    board_bmp.set_colorkey(c_transparent)
    background.blit(board_bmp, (0, 0))

    cells = [Cell('cell', x, c_transparent) for x in range(4)]
    foundations = [Cell('foundation', x, c_transparent) for x in range(4)]
    card_size = (58, 34)
    x_col_positions = [77 + x * (card_size[0] + 3) for x in range(8)]
    undo_pos = (0, 0)
    mouse_down_pos = (0, 0)
    click = True
    root_card = None

    cards = []
    for val in range(1, 14):
        for suit in ('spades', 'clubs', 'diamonds', 'hearts'):
            cards.append(
                Card(transparent=c_transparent, value=val, suit=suit))
    random.shuffle(cards)
    set_card_positions(cards, x_col_positions)
    deal(cards, deal_event)

    is_running = True

    while is_running:
        clock.tick(60)
        fps = clock.get_fps()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False
            elif event.type == deal_event:
                deal(cards, deal_event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
                    mouse_down_pos = event.pos
                    card = get_selected_card(event, cards)
                    if card:
                        if is_draggable(card, cards):
                            undo_pos = (card.x, card.y)
                            card.dragging = True
                            root_card = card
                            print('root_card set')
                            card.drag_offset = (
                                event.pos[0] - card.x, event.pos[1] - card.y)
                            # Move card(s) to end of list to be blitted last
                            cards.append(cards.pop(cards.index(card)))
                            for tab_card in card.tableau:
                                cards.append(cards.pop(cards.index(tab_card)))
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    if event.pos == mouse_down_pos and click:
                        pass # TODO: Add automove
                    else:
                        target = get_selected_card(
                            event, [c for c in cards if not c.dragging])
                        if target and [c for c in cards if c.dragging]:
                            col = target.col
                            if is_valid_move(card, target, col, cards):
                                card.move(get_cascade_pos(cards, col), col)
                                target.tableau.append(card)
                            else:
                                # Undo move
                                print(f'Invalid move. Moving {root_card.label} back to {undo_pos}')
                                root_card.move(undo_pos)
                        else:
                            try:
                                # Undo move
                                root_card.move(undo_pos)
                            except IndexError:
                                pass # Wasn't dragging anything
                        cards = set_z_indexes(cards) # Reset draw order
                    for card in [c for c in cards if c.dragging]:
                        card.dragging = False
                    reset_tableaux(cards)
            elif event.type == pygame.MOUSEMOTION:
                click = False

        window_surface.blit(background, (0, 0))
        window_surface.blit(board_bmp, (0, 0))
        for cell in cells + foundations:
            window_surface.blit(cell.surf, (cell.x, cell.y))
        for card in cards:
            card.update(pygame.mouse.get_pos())
            window_surface.blit(card.surf, (card.x, card.y))

        pygame.display.update()

if __name__ == '__main__':
    main()
