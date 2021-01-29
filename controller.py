import pygame

class Controller(object):
    def __init__(self):
        self.pos = (0, 0)

        self.btn_a = {
            'name': 'A',
            'map': pygame.K_j, # Keyboard 'J'
            'pressed': False
        }
        self.btn_b = {
            'name': 'B',
            'map': pygame.K_i, # Keyboard 'I'
            'pressed': False
        }

        self.btn_dpad_u = {
            'name': 'D-PAD UP',
            'map': pygame.K_w, # Keyboard 'W'
            'pressed': False
        }
        self.btn_dpad_r = {
            'name': 'D-PAD RIGHT',
            'map': pygame.K_d, # Keyboard 'D'
            'pressed': False
        }
        self.btn_dpad_d = {
            'name': 'D-PAD DOWN',
            'map': pygame.K_s, # Keyboard 'S'
            'pressed': False
        }
        self.btn_dpad_l = {
            'name': 'D-PAD LEFT',
            'map': pygame.K_a, # Keyboard 'A'
            'pressed': False
        }

        self.btn_start = {
            'name': 'START',
            'map': pygame.K_SPACE, # Keyboard 'SPACE'
            'pressed': False
        }

        self.buttons = (self.btn_a, self.btn_b, self.btn_dpad_u, self.btn_dpad_r, self.btn_dpad_d, self.btn_dpad_l)

    def get_action_button(self, event):
        if event.type == pygame.KEYDOWN:
            try:
                btn = [b for b in self.buttons if b['map'] == event.key][0]
                if not btn['pressed']:
                    btn['pressed'] = True
                    return f'{btn["name"]} press'
            except IndexError:
                return None # Button/key not supported

        elif event.type == pygame.KEYUP:
            try:
                btn = [b for b in self.buttons if b['map'] == event.key][0]
                btn['pressed'] = False
                return f'{btn["name"]} release'
            except IndexError:
                return None # Button/key not supported

        return None # Not a keyboard event
