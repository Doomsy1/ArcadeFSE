import pygame
from utils import write_centered_text


buttons = {
    'player vs player': {
        'rect': pygame.Rect(300, 200, 200, 100),
        'action': 'player vs player'
    },
    'player vs computer': {
        'rect': pygame.Rect(300, 400, 200, 100),
        'action': 'player vs computer'
    },
    'chess settings': {
        'rect': pygame.Rect(300, 600, 200, 100),
        'action': 'chess settings menu'
    }
}


class ChessMainMenu:
    def __init__(self, screen):
        self.screen = screen

    def main_loop(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                # if the player presses escape, return to the main menu
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return 'exit'

            self.screen.fill((0, 0, 0)) # replace this with a background image

            for button in buttons:
                pygame.draw.rect(self.screen, (255, 255, 255), buttons[button]['rect'])
                write_centered_text(self.screen, button, buttons[button]['rect'], (0, 0, 0))

            # check if the player clicked on a button
            if pygame.mouse.get_pressed()[0]:
                for button in buttons:
                    if buttons[button]['rect'].collidepoint(pygame.mouse.get_pos()):
                        return buttons[button]['action']

            pygame.display.flip()

        return 'exit'