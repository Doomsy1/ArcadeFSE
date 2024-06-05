from constants import PACMAN_VEL, PACMAN_GRID_SIZE, PACMAN_X_OFFSET, PACMAN_Y_OFFSET
import pygame


class PacmanPlayer:
    def __init__(self, screen, map):
        self.screen = screen
        self.current_direction = 'stopped'
        self.queue_direction = 'stopped'
        self.map = map

        self.x = PACMAN_GRID_SIZE * 9 + PACMAN_X_OFFSET
        self.y = PACMAN_GRID_SIZE * 11 + PACMAN_Y_OFFSET

        self.powered_up = False
        self.score = 0
        
    def handle_keys(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                # up arrow key down
                if event.key == pygame.K_UP:
                    self.queue_direction = 'up'
                # down arrow key down
                if event.key == pygame.K_DOWN:
                    self.queue_direction = 'down'
                # left arrow key down
                if event.key == pygame.K_LEFT:
                    self.queue_direction = 'left'
                # right arrow key down
                if event.key == pygame.K_RIGHT:
                    self.queue_direction = 'right'

    def draw_queued_direction(self):
        if self.queue_direction == 'up':
            pygame.draw.rect(self.screen, (0, 255, 0), (self.x, self.y - 10, PACMAN_GRID_SIZE, 10))
        if self.queue_direction == 'down':
            pygame.draw.rect(self.screen, (0, 255, 0), (self.x, self.y + PACMAN_GRID_SIZE, PACMAN_GRID_SIZE, 10))
        if self.queue_direction == 'left':
            pygame.draw.rect(self.screen, (0, 255, 0), (self.x - 10, self.y, 10, PACMAN_GRID_SIZE))
        if self.queue_direction == 'right':
            pygame.draw.rect(self.screen, (0, 255, 0), (self.x + PACMAN_GRID_SIZE, self.y, 10, PACMAN_GRID_SIZE))

    def draw(self):
        pygame.draw.rect(self.screen, (255, 255, 0), (self.x, self.y, PACMAN_GRID_SIZE, PACMAN_GRID_SIZE))
        # self.draw_queued_direction() # debug

    def can_move(self, direction):
        if direction == 'stopped':
            return False
        if direction == 'up':
            future_x, future_y = self.x, self.y - PACMAN_VEL
        if direction == 'down':
            future_x, future_y = self.x, self.y + PACMAN_VEL
        if direction == 'left':
            future_x, future_y = self.x - PACMAN_VEL, self.y
        if direction == 'right':
            future_x, future_y = self.x + PACMAN_VEL, self.y

        future_rect = pygame.Rect(future_x, future_y, PACMAN_GRID_SIZE, PACMAN_GRID_SIZE)
        return self.map.is_wall(future_rect) == False

    def move(self):
        if self.current_direction == 'up':
            self.y -= PACMAN_VEL
        if self.current_direction == 'down':
            self.y += PACMAN_VEL
        if self.current_direction == 'left':
            self.x -= PACMAN_VEL
        if self.current_direction == 'right':
            self.x += PACMAN_VEL

    def update(self):
        # if the player is able to move in the queue direction then update the current direction
        if self.can_move(self.queue_direction):
            self.current_direction = self.queue_direction
        if self.can_move(self.current_direction):
            self.move()
        pacman_rect = pygame.Rect(self.x, self.y, PACMAN_GRID_SIZE, PACMAN_GRID_SIZE)
        # eat pellets if the player is on top of them
        if self.map.is_pellet(pacman_rect):
            self.map.remove_pellet(pacman_rect)
            self.score += 1
            print(self.score) 
        # eat powerups if the player is on top of them
        if self.map.is_powerup(pacman_rect):
            self.map.remove_powerup(pacman_rect)
            self.powered_up = True