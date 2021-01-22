import math, random
import pygame
from card import Card
from cell import Cell

def autocomplete(cards, cells, foundations):
    print('---Begin autocomplete---')

    card_moved = True
    while card_moved:
        card_moved = False
        for suit in ('spades', 'clubs', 'diamonds', 'hearts'):
            suit_cards = [c for c in cards if c.on_foundation and c.suit == suit]
            if suit_cards:
                high_card = sorted(suit_cards, key=lambda c: c.value, reverse=True)[0]
                print(f'    High card on {suit} foundation: {high_card.label}')
                try:
                    target = [c for c in cards if c.suit == suit and c.value == high_card.value + 1][0]
                except IndexError:
                    print(f'All {suit} already on foundation')
                    break
                print(f'    Target: {target.label}')
                if target.on_cell:
                    print('    Target on cell')
                    target.target_x = high_card.x
                    target.target_y = high_card.y
                    target.animating = True
                    print(f'    {target.label} targeting {suit} foundation on top of {high_card.label}')
                    card_moved = True
                    break
                else:
                    print('    Target not on cell')
                    if target.y == max([c.y for c in cards if c.col == target.col]):
                        target.move((high_card.x, high_card.y), to_foundation=True)
                        print(f'    {target.label} moved to {suit} foundation on top of {high_card.label}')
                        card_moved = True
                        break
            else:
                print(f'    No cards on {suit} foundation')
                target = [c for c in cards if c.suit == suit and c.value == 1][0]
                print(f'    Target: {target.label} in cascade #{target.col + 1}')
                foundation = [f for f in foundations if f.suit == suit][0]
                if target.on_cell:
                    print('    Target on cell')
                    target.move((foundation.x, foundation.y), to_foundation=True)
                    print(f'    {target.label} moved from cell to {suit} foundation base')
                    card_moved = True
                    break
                else:
                    print('    Target not on cell')
                    if target.y == max([c.y for c in cards if c.col == target.col]):
                        target.move((foundation.x, foundation.y), to_foundation=True)
                        print(f'{target.label} moved to {suit} foundation base')
                        card_moved = True
                        break
                    else:
                        print(f'    {target.label} is not at the bottom of its cascade')

    print('----End autocomplete----')

def automove(card, cards, cells, foundations, bases):
    # Ace to foundation
    if card.value == 1:
        print(f'Automove: {card.label} -> {card.suit} foundation')
        target = [f for f in foundations if f.suit == card.suit][0]
        card.move((target.x, target.y), to_foundation=True)
        return
    elif not card.tableau:
        cards_on_foundation = [c for c in cards if c.on_foundation and c.suit == card.suit]
        # Non-ace to foundation
        if cards_on_foundation:
            high_card = sorted(cards_on_foundation, key=lambda c: c.value, reverse=True)[0]
            if high_card.value == card.value - 1:
                print(f'Automove: {card.label} -> {card.suit} foundation')
                card.move((high_card.x, high_card.y), to_foundation=True)
                return
        # Card to valid cascade
        if make_valid_move(card, cards, cells, foundations, bases):
            print(f'Automove: {card.label} -> valid cascade card or empty base')
            return
        else:
            # Move to free cell
            free_cells = [c for c in cells if c.vacant]
            if free_cells:
                cell = free_cells[0]
                print(f'Automove: {card.label} -> cell #{cell.pos}')
                card.move((cell.x, cell.y), to_cell=True)
                return
            else:
                print('Automove: No valid targets')
                return
    else:
        if make_valid_move(card, cards, cells, foundations, bases):
            print(f'Automove: {card.label} + tableau -> valid cascade card or empty base')
            return
        else:
            print('Automove: No valid targets')

def close_menu():
    print('Menu closed')

def deal(deck, deal_event):
    card = [c for c in deck if not c.animating and not (c.x, c.y) == (c.target_x, c.target_y)]
    if card:
        card = card[0]
        card.animating = True
        pygame.time.set_timer(deal_event, 50, True)
    else:
        global DEALING
        DEALING = False

def make_valid_move(card, cards, cells, foundations, bases):
    print('make_valid_move(): Start')
    possible_moves = []
    for col in range(8):
        if col == card.col:
            continue
        col_cards = [c for c in cards if c.col == col]
        try:
            possible_moves.append(sorted(col_cards, key=lambda c: c.y, reverse=True)[0])
        except IndexError:
            # No cards in column; add base instead
            possible_moves.append([b for b in bases if b.col == col][0])
    print(f'make_valid_move(): {card.label} ? {", ".join([c.label if c in cards  else "[base]" for c in possible_moves])}')
    for target in [t for t in possible_moves if t not in bases]:
        if not target.color == card.color and target.value == card.value + 1:
            print(f'make_valid_move(): {card.label} -> {target.label}, col={target.col}')
            card.move(get_cascade_pos(cards, target), target.col)
            return True
    for target in [t for t in possible_moves if t in bases]:
        if is_valid_move(card, target, cards, cells, foundations, bases):
            print(f'make_valid_move(): {card.label} -> cascade base (col={target.col})')
            card.move((target.x, target.y), target.col)
            return True
    print('make_valid_move(): No valid move to make')
    return False

def get_cascade_pos(cards, target):
    bottom_card = [c for c in cards if c.col == target.col][-1]
    return (bottom_card.x, bottom_card.y + 18)

def get_move_target(event, cards, cells, foundations, bases):
    cards_under_cursor = [c for c in cards if c.rect.collidepoint(event.pos)]
    print(f'Cards under cursor: {", ".join([c.label for c in cards_under_cursor])}')
    if cards_under_cursor:
        if cards_under_cursor[0].on_foundation:
            # Sort foundation cards by value; take highest
            cards_under_cursor = sorted(cards_under_cursor, key=lambda c: c.value, reverse=True)
        else:
            # Sort non-foundation cards by y position; take highest
            cards_under_cursor = sorted(cards_under_cursor, key=lambda c: c.y, reverse=True)
        return cards_under_cursor[0]
    cells_under_cursor = [c for c in cells if c.rect.collidepoint(event.pos)]
    if cells_under_cursor:
        return cells_under_cursor[0]
    foundations_under_cursor = [c for c in foundations if c.rect.collidepoint(event.pos)]
    if foundations_under_cursor:
        return foundations_under_cursor[0]
    bases_under_cursor = [c for c in bases if c.rect.collidepoint(event.pos)]
    if bases_under_cursor:
        return bases_under_cursor[0]
    return None

def get_max_draggable_tableau(cards, to_base = 0):
    empty_cols = 0
    for n in range(8):
        if not [c for c in cards if c.col == n]:
            empty_cols += 1
    return (5 - len([c for c in cards if c.on_cell])) * (empty_cols - to_base + 1)

def is_draggable(card, cards):
    if not card in cards:
        print('Invalid drag (not a card)')
        return False
    if card.on_cell or card.on_foundation:
        print('Valid card drag (on cell or foundation)')
        return True
    # Bottom card in cascade
    if card == [c for c in cards if c.col == card.col][-1]:
        print('Valid card drag (bottom of cascade)')
        return True
    # Non-bottom card, but all below are in a tableau
    cards_below = len([c for c in cards if c.col == card.col and c.y > card.y])
    # return bool(len(card.tableau) == cards_below)
    if len(card.tableau) == cards_below:
        if len(card.tableau) + 1 <= get_max_draggable_tableau(cards):
            print('Valid card drag (root of bottom tableau)')
            return True
        else:
            print(f'Invalid card drag (tableau size: {len(card.tableau) + 1}; only {get_max_draggable_tableau(cards)} can be moved)')
            return False
    else:
        print(f'Invalid card drag ({len(card.tableau)} cards in tableau; {cards_below} cards below target: {", ".join([c2.label for c2 in [c for c in cards if c.col == card.col and c.y > card.y]])})')
        return False

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

def reset_tableaux_and_cells(cards, cells):
    # print('---New tableaux---')
    for cell in cells:
        cell.vacant = True
    for card in cards:
        card.tableau = []
        cards_below = [c for c in cards if c.col == card.col and c.target_y > card.target_y and not c.on_foundation and not c.on_cell]
        for n in range(len(cards_below)):
            child = cards_below[n]
            parent = cards_below[n - 1] if n else card
            if child.value == parent.value - 1 and not child.color == parent.color:
                card.tableau.append(child)
            else:
                break
        if card.on_cell:
            try:
                cell = [c for c in cells if c.rect.colliderect(card.rect)][0]
                cell.vacant = False
            except IndexError:
                print(f'ERROR: {card.label}.on_cell = True; cannot find occupied cell')

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

def win():
    global GAME_IN_PROGRESS
    GAME_IN_PROGRESS = False
    print('You win!')

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

    global INPUT_ENABLED
    global GAME_IN_PROGRESS
    global PAUSED
    global DEALING
    INPUT_ENABLED = False
    GAME_IN_PROGRESS = True
    PAUSED = False
    DEALING = True

    deck_pos = (291, 190)
    card_back = pygame.image.load('card_back.bmp')
    card_back.set_colorkey(c_transparent)

    suits = ('spades', 'clubs', 'diamonds', 'hearts')
    cells = [Cell('cell', x, c_transparent) for x in range(4)]
    foundations = [Cell('foundation', x, c_transparent, suits[x]) for x in range(4)]
    card_size = (58, 34)
    x_col_positions = [77 + x * (card_size[0] + 3) for x in range(8)]
    bases = [Cell('base', x_col_positions[x], c_transparent, col=x) for x in range(8)]
    undo_pos = (0, 0)
    mouse_down_pos = (0, 0)
    click = True
    root_card = None

    cards = []
    for val in range(1, 14):
        for suit in suits:
            cards.append(
                Card(pos=deck_pos, transparent=c_transparent, value=val, suit=suit))
    random.shuffle(cards)
    set_card_positions(cards, x_col_positions)
    deal(cards, deal_event)
    reset_tableaux_and_cells(cards, cells)

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
                if INPUT_ENABLED and GAME_IN_PROGRESS:
                    if event.button == 1:
                        click = True
                        mouse_down_pos = event.pos
                        root_card = None
                        card = get_move_target(event, cards, cells, foundations, bases)
                        if card:
                            if card in cards and not card.col == None:
                                print(f'Mouse down on {card.label} in cascade #{card.col + 1} (col={card.col})')
                            if is_draggable(card, cards):
                                undo_pos = (card.x, card.y)
                                card.dragging = True
                                root_card = card
                                card.drag_offset = (
                                    event.pos[0] - card.x, event.pos[1] - card.y)
                                # Move card(s) to end of list to be blitted last
                                cards.append(cards.pop(cards.index(card)))
                                for tab_card in card.tableau:
                                    cards.append(cards.pop(cards.index(tab_card)))
                            else:
                                print('Card is not draggable')
                                root_card = None
            elif event.type == pygame.MOUSEBUTTONUP:
                if INPUT_ENABLED and GAME_IN_PROGRESS:
                    if event.button == 1:
                        if event.pos == mouse_down_pos and click and root_card:
                            automove(root_card, cards, cells, foundations, bases)
                        else:
                            target = get_move_target(
                                event, [c for c in cards if not c.dragging], cells, foundations, bases)
                            if target and [c for c in cards if c.dragging]:
                                if is_valid_move(root_card, target, cards, cells, foundations, bases):
                                    # Non-card targets
                                    if target in foundations:
                                        root_card.move((target.x, target.y), to_foundation=True)
                                    elif target in cells:
                                        root_card.move((target.x, target.y), to_cell=True)
                                    elif target in bases:
                                        root_card.move((target.x, target.y), target.col)
                                    # Card targets
                                    elif target.on_foundation:
                                        root_card.move((target.x, target.y), to_foundation=True)
                                    else:
                                        root_card.move(get_cascade_pos(cards, target), target.col)
                                else:
                                    # Undo move
                                    root_card.move(undo_pos, card.col)
                            else:
                                try:
                                    # Undo move
                                    root_card.move(undo_pos, card.col)
                                    print('Undid move with no target')
                                except AttributeError:
                                    print('No move to undo')
                                    pass # Wasn't dragging anything
                            cards = set_z_indexes(cards) # Reset draw order
                        for card in [c for c in cards if c.dragging]:
                            card.dragging = False
                        reset_tableaux_and_cells(cards, cells)
                    # Win condition
                    if len([c for c in cards if c.on_foundation]) == len(cards):
                        win()
            elif event.type == pygame.MOUSEMOTION:
                if INPUT_ENABLED and GAME_IN_PROGRESS:
                    click = False
            elif event.type == pygame.KEYDOWN:
                if INPUT_ENABLED:
                    if event.key == pygame.K_SPACE:
                        if PAUSED:
                            PAUSED = False
                            close_menu()
                        else:
                            PAUSED = True
                            open_menu()
                    elif event.key == pygame.K_s:
                        if PAUSED:
                            autocomplete(cards, cells, foundations)

        window_surface.blit(background, (0, 0))
        window_surface.blit(board_bmp, (0, 0))
        for base in bases:
            window_surface.blit(base.surf, (base.x, base.y))
        for cell in cells + foundations:
            window_surface.blit(cell.surf, (cell.x, cell.y))
        for card in cards:
            card.update(pygame.mouse.get_pos())
            window_surface.blit(card.surf, (card.x, card.y))
        if DEALING:
            window_surface.blit(card_back, deck_pos)
        # Wait for animation
        INPUT_ENABLED = not bool(len([c for c in cards if c.animating]))
        pygame.display.update()

if __name__ == '__main__':
    main()

"""
TODO
----

- Menu
    - Restart
    - New game
- Restack cards when cascades too long to fit on screen
- Update 'drop' placement of drag-and-drop so cursor doesn't need to be over target card
- Controller support
- Big refactor

"""
