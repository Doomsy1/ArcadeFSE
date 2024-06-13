from constants import PACMAN_GRID_SIZE, PACMAN_X_OFFSET, PACMAN_Y_OFFSET
import pygame

# 0: empty
# 1: wall
# 2: pellet (empty)
# 3: powerup (empty)

map_grid = [
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 3, 1, 1, 2, 1, 1, 1, 2, 1, 2, 1, 1, 1, 2, 1, 1, 3, 1],
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 2, 1],
    [1, 2, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 2, 1, 1, 1, 0, 1, 0, 1, 1, 1, 2, 1, 1, 1, 1],
    [0, 0, 0, 1, 2, 1, 0, 0, 0, 0, 0, 0, 0, 1, 2, 1, 0, 0, 0],
    [1, 1, 1, 1, 2, 1, 0, 1, 1, 4, 1, 1, 0, 1, 2, 1, 1, 1, 1],
    [0, 0, 0, 0, 2, 0, 0, 1, 0, 0, 0, 1, 0, 0, 2, 0, 0, 0, 0],
    [1, 1, 1, 1, 2, 1, 0, 1, 1, 1, 1, 1, 0, 1, 2, 1, 1, 1, 1],
    [0, 0, 0, 1, 2, 1, 0, 0, 0, 0, 0, 0, 0, 1, 2, 1, 0, 0, 0],
    [1, 1, 1, 1, 2, 1, 0, 1, 1, 1, 1, 1, 0, 1, 2, 1, 1, 1, 1],
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 2, 1, 1, 2, 1, 1, 1, 2, 1, 2, 1, 1, 1, 2, 1, 1, 2, 1],
    [1, 3, 2, 1, 2, 2, 2, 2, 2, 0, 2, 2, 2, 2, 2, 1, 2, 3, 1],
    [1, 1, 2, 1, 2, 1, 2, 1, 1, 1, 1, 1, 2, 1, 2, 1, 2, 1, 1],
    [1, 2, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2, 2, 1, 2, 2, 2, 2, 1],
    [1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1],
    [1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
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
                cell_rect = pygame.Rect(x * PACMAN_GRID_SIZE, y * PACMAN_GRID_SIZE, PACMAN_GRID_SIZE, PACMAN_GRID_SIZE)

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

                    # gate
                    case 4:
                        self.gate_rect = cell_rect

        return map_image
    
    def draw(self):
        '''Draw the map image to the screen and the pellets and powerups'''
        
        self.screen.blit(self.map_image, (PACMAN_X_OFFSET, PACMAN_Y_OFFSET))

        for pellet in self.pellets:
            x = pellet[0] + PACMAN_X_OFFSET
            y = pellet[1] + PACMAN_Y_OFFSET
            pygame.draw.circle(self.screen, PELLET_COLOR, (x, y), PELLET_RADIUS)

        for powerup in self.powerups:
            x = powerup[0] + PACMAN_X_OFFSET
            y = powerup[1] + PACMAN_Y_OFFSET
            pygame.draw.circle(self.screen, POWERUP_COLOR, (x, y), POWERUP_RADIUS)

    def is_wall(self, rect):
        '''Check if the given x, y coordinates are a wall'''
        rect = rect.move(-PACMAN_X_OFFSET, -PACMAN_Y_OFFSET)
        for wall in self.wall_rects:
            if wall.colliderect(rect):
                return True
        return False
    
    def is_gate(self, rect):
        '''Check if the given x, y coordinates are a gate'''
        rect = rect.move(-PACMAN_X_OFFSET, -PACMAN_Y_OFFSET)
        return self.gate_rect.colliderect(rect)
    
    def is_wall_at_pos(self, x, y):
        if x < 0 or y < 0 or x >= len(map_grid[0]) or y >= len(map_grid):
            return True
        return map_grid[y][x] == 1
    
    def is_pellet(self, rect):
        '''Check if the given x, y coordinates are a pellet'''
        for pellet in self.pellets:
            pellet_x = pellet[0] - PELLET_RADIUS + PACMAN_X_OFFSET
            pellet_y = pellet[1] - PELLET_RADIUS + PACMAN_Y_OFFSET
            if pygame.Rect(pellet_x, pellet_y, PELLET_RADIUS * 2, PELLET_RADIUS * 2).colliderect(rect):
                return True
        return False
    
    def is_powerup(self, rect):
        '''Check if the given x, y coordinates are a powerup'''
        for powerup in self.powerups:   
            powerup_x = powerup[0] - POWERUP_RADIUS + PACMAN_X_OFFSET
            powerup_y = powerup[1] - POWERUP_RADIUS + PACMAN_Y_OFFSET
            if pygame.Rect(powerup_x, powerup_y, POWERUP_RADIUS * 2, POWERUP_RADIUS * 2).colliderect(rect):
                return True
        return False
    
    def remove_pellet(self, rect):
        '''Remove the pellet at the given x, y coordinates'''
        for pellet in self.pellets:
            pellet_x = pellet[0] - PELLET_RADIUS + PACMAN_X_OFFSET
            pellet_y = pellet[1] - PELLET_RADIUS + PACMAN_Y_OFFSET
            if pygame.Rect(pellet_x, pellet_y, PELLET_RADIUS * 2, PELLET_RADIUS * 2).colliderect(rect):
                self.pellets.remove(pellet)
                return

    def remove_powerup(self, rect):
        '''Remove the powerup at the given x, y coordinates'''
        for powerup in self.powerups:
            powerup_x = powerup[0] - POWERUP_RADIUS + PACMAN_X_OFFSET
            powerup_y = powerup[1] - POWERUP_RADIUS + PACMAN_Y_OFFSET
            if pygame.Rect(powerup_x, powerup_y, POWERUP_RADIUS * 2, POWERUP_RADIUS * 2).colliderect(rect):
                self.powerups.remove(powerup)
                return
            
    def get_pos(self, rect):
        '''Get the index on the map grid of the center of the given rect'''
        x = rect.centerx - PACMAN_X_OFFSET
        y = rect.centery - PACMAN_Y_OFFSET
        x_pos = x // PACMAN_GRID_SIZE
        y_pos = y // PACMAN_GRID_SIZE

        y_pos = min(len(map_grid) - 1, y_pos)
        y_pos = max(0, y_pos)

        x_pos = min(len(map_grid[0]) - 1, x_pos)
        x_pos = max(0, x_pos)

        return x_pos, y_pos
    
    def is_level_complete(self):
        '''Check if the level is complete'''
        return len(self.pellets) == 0

    @staticmethod
    def get_distance(p1, p2):
        '''Get the distance between two points'''
        return ((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2) ** 0.5