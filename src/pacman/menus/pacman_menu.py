import pygame
from utils import Button


buttons = {
    'pacman': {
        'text': 'Pacman',
        'rect': pygame.Rect(300, 300, 200, 100),
        'action': 'pacman',
        'base_color': (0, 206, 209),
        'hover_color': (64, 224, 208),
        'clicked_color': (0, 139, 139),
        'text_color': (255, 255, 255),
        'description': 'Play Pacman'
    },
    'leaderboard': {
        'text': 'Leaderboard',
        'rect': pygame.Rect(300, 480, 200, 100),
        'action': 'pacman leaderboard',
        'base_color': (0, 206, 209),
        'hover_color': (64, 224, 208),
        'clicked_color': (0, 139, 139),
        'text_color': (255, 255, 255),
        'description': 'View the Pacman leaderboard'
    },
    'back': {
        'text': 'Back',
        'rect': pygame.Rect(300, 860, 200, 100),
        'action': 'exit',
        'base_color': (0, 206, 209),
        'hover_color': (64, 224, 208),
        'clicked_color': (0, 139, 139),
        'text_color': (255, 255, 255),
        'description': 'Return to the main menu'
    }
}

class PacmanMenu:
    def __init__(self, screen):
        self.screen = screen

        self.load_background()

        self.create_buttons()

    def create_buttons(self):
        self.buttons = []
        for button in buttons:
            button = Button(
                screen = self.screen,
                text = buttons[button]['text'],
                rect = buttons[button]['rect'],
                action = buttons[button]['action'],
                base_color = buttons[button]['base_color'],
                hover_color = buttons[button]['hover_color'],
                clicked_color = buttons[button]['clicked_color'],
                text_color = buttons[button]['text_color'],
                descriptive_text = buttons[button]['description']
            )
            self.buttons.append(button)

    def load_background(self):
        background_path = "assets\PacmanBackground.png"

        self.background = pygame.image.load(background_path)

        # scale the image to fit the screen (760x1000)
        # scale to 1000x1000
        self.background = pygame.transform.scale(self.background, (1000, 1000))

    def draw_background(self):
        # center the background on the center of the screen
        screen_width, screen_height = self.screen.get_width(), self.screen.get_height()

        background_width, background_height = self.background.get_width(), self.background.get_height()

        x = (screen_width - background_width) / 2
        y = (screen_height - background_height) / 2

        self.screen.blit(self.background, (x, y))

    def main_loop(self):
        running = True

        while running:
            L_mouse_up = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit"
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        L_mouse_up = True

            mx, my = pygame.mouse.get_pos()
            mb = pygame.mouse.get_pressed()

            # draw the background
            self.draw_background()

            # draw the game buttons
            for button in self.buttons:
                button.draw(mx, my, mb)

            # check if the left mouse button is released
            for button in self.buttons:
                action = button.check_click(mx, my, L_mouse_up)
                if action:
                    return action
                    
            pygame.display.flip()

        return 'exit'