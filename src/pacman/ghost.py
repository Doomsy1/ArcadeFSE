import random
from constants import PACMAN_GRID_SIZE, PACMAN_X_OFFSET, PACMAN_Y_OFFSET, GHOST_VEL
import pygame
from src.pacman.map import map_grid


class Ghost:
    def __init__(self, screen, map, pacman): # TODO: add color to differentiate ghosts
        self.screen = screen
        self.current_direction = 'stopped'
        self.map = map

        self.x = PACMAN_GRID_SIZE * 9 + PACMAN_X_OFFSET
        self.y = PACMAN_GRID_SIZE * 7 + PACMAN_Y_OFFSET

        self.pacman = pacman

    def draw(self, pacman_powered_up=False):
        if pacman_powered_up:
            pygame.draw.rect(self.screen, (0, 255, 0), (self.x, self.y, PACMAN_GRID_SIZE, PACMAN_GRID_SIZE))
        else:
            pygame.draw.rect(self.screen, (255, 0, 0), (self.x, self.y, PACMAN_GRID_SIZE, PACMAN_GRID_SIZE))

    def get_possible_directions(self):
        possible_directions = []
        for direction in ['up', 'down', 'left', 'right']:
            # the ghost can't move in the opposite direction
            if direction == 'up' and self.current_direction == 'down':
                continue
            if direction == 'down' and self.current_direction == 'up':
                continue
            if direction == 'left' and self.current_direction == 'right':
                continue
            if direction == 'right' and self.current_direction == 'left':
                continue
            if self.can_move(direction):
                possible_directions.append(direction)
        return possible_directions

    def can_move(self, direction):
        if direction == 'stopped':
            return False
        if direction == 'up':
            future_x, future_y = self.x, self.y - GHOST_VEL
        if direction == 'down':
            future_x, future_y = self.x, self.y + GHOST_VEL
        if direction == 'left':
            future_x, future_y = self.x - GHOST_VEL, self.y
        if direction == 'right':
            future_x, future_y = self.x + GHOST_VEL, self.y

        future_rect = pygame.Rect(future_x, future_y, PACMAN_GRID_SIZE, PACMAN_GRID_SIZE)
        return not self.map.is_wall(future_rect)

    def update(self, pacman_powered_up=False):
        if self.at_intersection():
            if not pacman_powered_up:
                self.current_direction = self.get_best_direction()
            else:
                # move randomly if the pacman is powered up (temporary solution)
                self.current_direction = random.choice(self.get_possible_directions())
        self.move()

    def get_best_direction(self):
        '''Use bfs to find the best direction to move in'''
        pacman_pos = self.map.get_pos(self.pacman.pacman_rect)
        current_x = (self.x - PACMAN_X_OFFSET) // PACMAN_GRID_SIZE
        current_y = (self.y - PACMAN_Y_OFFSET) // PACMAN_GRID_SIZE
        visited = set()
        queue = [(current_x, current_y)]
        parent = {}

        while queue:
            x, y = queue.pop(0)
            if (x, y) == pacman_pos:
                break
            visited.add((x, y))
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                new_x, new_y = x + dx, y + dy
                if (new_x, new_y) in visited:
                    continue
                if self.map.is_wall_at_pos(new_x, new_y):
                    continue
                queue.append((new_x, new_y))
                parent[(new_x, new_y)] = (x, y)

        # find the best direction to move in
        while (current_x, current_y) != pacman_pos:
            dx, dy = pacman_pos[0] - current_x, pacman_pos[1] - current_y
            pacman_pos = parent[pacman_pos]


        print(dx, dy)
        if dx == 1:
            return 'right'
        if dx == -1:
            return 'left'
        if dy == 1:
            return 'down'
        if dy == -1:
            return 'up'

    def at_intersection(self):
        # check if the ghost is exactly on a grid
        if (self.x - PACMAN_X_OFFSET) % PACMAN_GRID_SIZE != 0:
            return False
        if (self.y - PACMAN_Y_OFFSET) % PACMAN_GRID_SIZE != 0:
            return False
        
        # check if the ghost is at an intersection (can't continue straight or 3 possible directions)
        possible_directions = self.get_possible_directions()
        if self.current_direction not in possible_directions:
            return True
        
        return len(possible_directions) > 1

    def move(self):
        if self.current_direction == 'up':
            self.y -= GHOST_VEL
        if self.current_direction == 'down':
            self.y += GHOST_VEL
        if self.current_direction == 'left':
            self.x -= GHOST_VEL
        if self.current_direction == 'right':
            self.x += GHOST_VEL