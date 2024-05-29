from constants import PACMAN_GRID_SIZE, PACMAN_X_OFFSET, PACMAN_Y_OFFSET
import pygame

# 0: empty
# 1: wall
# 2: pellet (empty)
# 3: powerup (empty)

map_grid = [
    [1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 1],
    [1, 2, 1, 1, 1, 2, 1],
    [1, 2, 0, 3, 0, 2, 1],
    [1, 2, 1, 1, 1, 2, 1],
    [1, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1]
]

EMPTY_COLOR = (0, 0, 0)
WALL_COLOR = (0, 0, 255)
PELLET_COLOR = (255, 255, 255)
PELLET_RADIUS = 4
POWERUP_COLOR = (255, 127, 127)
POWERUP_RADIUS = 8

class PacmanMap:
    def __init__(self, screen):
        self.screen = screen
        self.wall_rects = []
        self.pellets = []
        self.powerups = []

        self.map_image = self.create_image()
        
    def create_image(self):
        '''Create the map image and wall rects'''

        map_image = pygame.Surface((len(map_grid[0]) * PACMAN_GRID_SIZE, len(map_grid) * PACMAN_GRID_SIZE))
        for y, row in enumerate(map_grid):
            for x, cell in enumerate(row):
                cell_rect = pygame.Rect(x * PACMAN_GRID_SIZE + PACMAN_X_OFFSET, y * PACMAN_GRID_SIZE + PACMAN_Y_OFFSET, PACMAN_GRID_SIZE, PACMAN_GRID_SIZE)

                match cell:
                    # empty
                    case 0:
                        pygame.draw.rect(map_image, EMPTY_COLOR, cell_rect)

                    # wall
                    case 1:
                        pygame.draw.rect(map_image, WALL_COLOR, cell_rect)
                        self.wall_rects.append(cell_rect)

                    # pellet
                    case 2:
                        pellet_pos = cell_rect.center
                        self.pellets.append(pellet_pos)

                    # powerup
                    case 3:
                        powerup_pos = cell_rect.center
                        self.powerups.append(powerup_pos)

        return map_image
    
    def draw(self):
        '''Draw the map image to the screen and the pellets and powerups'''
        
        self.screen.blit(self.map_image, (0, 0))

        for pellet in self.pellets:
            pygame.draw.circle(self.screen, PELLET_COLOR, pellet, PELLET_RADIUS)

        for powerup in self.powerups:
            pygame.draw.circle(self.screen, POWERUP_COLOR, powerup, POWERUP_RADIUS)

    def is_wall(self, x, y):
        '''Check if the given x, y coordinates are a wall'''
        for wall in self.wall_rects:
            if wall.collidepoint(x, y):
                return True
        return False
    
    def is_pellet(self, x, y):
        '''Check if the given x, y coordinates are a pellet'''
        for pellet in self.pellets:
            if pygame.Rect(pellet[0] - PELLET_RADIUS, pellet[1] - PELLET_RADIUS, PELLET_RADIUS * 2, PELLET_RADIUS * 2).collidepoint(x, y):
                return True
        return False
    
    def is_powerup(self, x, y):
        '''Check if the given x, y coordinates are a powerup'''
        for powerup in self.powerups:
            if pygame.Rect(powerup[0] - POWERUP_RADIUS, powerup[1] - POWERUP_RADIUS, POWERUP_RADIUS * 2, POWERUP_RADIUS * 2).collidepoint(x, y):
                return True
        return False
    
    def remove_pellet(self, x, y):
        '''Remove the pellet at the given x, y coordinates'''
        for pellet in self.pellets:
            if pygame.Rect(pellet[0] - PELLET_RADIUS, pellet[1] - PELLET_RADIUS, PELLET_RADIUS * 2, PELLET_RADIUS * 2).collidepoint(x, y):
                self.pellets.remove(pellet)
                return

    def remove_powerup(self, x, y):
        '''Remove the powerup at the given x, y coordinates'''
        for powerup in self.powerups:
            if pygame.Rect(powerup[0] - POWERUP_RADIUS, powerup[1] - POWERUP_RADIUS, POWERUP_RADIUS * 2, POWERUP_RADIUS * 2).collidepoint(x, y):
                self.powerups.remove(powerup)
                return