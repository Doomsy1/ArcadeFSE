from constants import PACMAN_STARTING_VEL
import pygame


class PacmanPlayer:
    def __init__(self, screen, map_grid):
        self.screen = screen
        self.current_direction = 'stopped'
        self.queue_direction = 'stopped'
        self.map_grid = map_grid
        
    def handle_keys(self):
        for event in pygame.event.get():
            # up arrow key
            if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                self.queue_direction = 'up'
            # down arrow key
            if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                self.queue_direction = 'down'
            # left arrow key
            if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                self.queue_direction = 'left'
            # right arrow key
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                self.queue_direction = 'right'

    def can_move(self, direction):
        True

    def update(self):
        # if the player is able to move in the queue direction then update the current direction
        if self.can_move(self.queue_direction):
            self.current_direction = self.queue_direction