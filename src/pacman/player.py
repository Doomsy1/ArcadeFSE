from constants import PACMAN_VEL, PACMAN_GRID_SIZE, PACMAN_X_OFFSET, PACMAN_Y_OFFSET
import pygame

START_POS = (9, 15)


class PacmanPlayer:
    def __init__(self, screen, map, score=0):
        self.screen = screen
        self.current_direction = 'stopped'
        self.queue_direction = 'stopped'
        self.map = map

        self.x = PACMAN_GRID_SIZE * START_POS[0] + PACMAN_X_OFFSET
        self.y = PACMAN_GRID_SIZE * START_POS[1] + PACMAN_Y_OFFSET

        self.powered_up = False

        self.score = score

        self.rect = pygame.Rect(self.x, self.y, PACMAN_GRID_SIZE, PACMAN_GRID_SIZE)

        self.load_animations()

        self.tick = 0

    def load_animations(self):
        self.animations = {
            'up': [],
            'down': [],
            'left': [],
            'right': []
        }

        for i in range(3):
            # load the images
            image = pygame.image.load(f'src\pacman\\assets\pacman\pacman{i}.png')

            # scale the image
            image = pygame.transform.scale(image, (PACMAN_GRID_SIZE, PACMAN_GRID_SIZE))

            # the image is facing right
            self.animations['right'].append(image)

            # rotate the image to face up
            image = pygame.transform.rotate(image, 90)
            self.animations['up'].append(image)

            # rotate the image to face left
            image = pygame.transform.rotate(image, 90)
            self.animations['left'].append(image)

            # rotate the image to face down
            image = pygame.transform.rotate(image, 90)
            self.animations['down'].append(image)

    def reset(self):
        self.x = PACMAN_GRID_SIZE * START_POS[0] + PACMAN_X_OFFSET
        self.y = PACMAN_GRID_SIZE * START_POS[1] + PACMAN_Y_OFFSET
        self.current_direction = 'stopped'
        self.queue_direction = 'stopped'
        self.rect = pygame.Rect(self.x, self.y, PACMAN_GRID_SIZE, PACMAN_GRID_SIZE)
        
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

    def draw_death(self, index):
        self.screen.blit(self.animations['up'][index], (self.x, self.y))

    def draw(self):
        if self.current_direction == 'stopped':
            self.screen.blit(self.animations['right'][1], (self.x, self.y))
        else:
            if self.can_move(self.queue_direction):
                self.screen.blit(self.animations[self.current_direction][self.tick // 5], (self.x, self.y))
                self.tick = (self.tick + 1) % 15
            else:
                self.screen.blit(self.animations[self.current_direction][1], (self.x, self.y))

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
        if direction == 'down' and self.map.is_gate(future_rect):
            return False
        
        return not self.map.is_wall(future_rect)

    def move(self):
        if self.current_direction == 'up':
            self.y -= PACMAN_VEL
        if self.current_direction == 'down':
            self.y += PACMAN_VEL
        if self.current_direction == 'left':
            self.x -= PACMAN_VEL
        if self.current_direction == 'right':
            self.x += PACMAN_VEL

        # wrap around the screen
        if self.x <= PACMAN_X_OFFSET - PACMAN_GRID_SIZE:
            self.x = PACMAN_X_OFFSET + PACMAN_GRID_SIZE * 19 - PACMAN_VEL
        if self.x >= PACMAN_X_OFFSET + PACMAN_GRID_SIZE * 19:
            self.x = PACMAN_X_OFFSET - PACMAN_GRID_SIZE + PACMAN_VEL

    def update(self):
        # if the player is able to move in the queue direction then update the current direction
        if self.can_move(self.queue_direction):
            self.current_direction = self.queue_direction
        if self.can_move(self.current_direction):
            self.move()
        self.rect = pygame.Rect(self.x, self.y, PACMAN_GRID_SIZE, PACMAN_GRID_SIZE)

        pellet_eaten = False
        # eat pellets if the player is on top of them
        if self.map.is_pellet(self.rect):
            pellet_eaten = True
            self.map.remove_pellet(self.rect)
            self.score += 10
        # eat powerups if the player is on top of them
        if self.map.is_powerup(self.rect):
            self.map.remove_powerup(self.rect)
            self.powered_up = True

        return pellet_eaten