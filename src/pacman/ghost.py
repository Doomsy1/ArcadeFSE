import random
from constants import PACMAN_GRID_SIZE, PACMAN_X_OFFSET, PACMAN_Y_OFFSET, GHOST_VEL
import pygame
from src.pacman.map import map_grid


class Ghost:
    def __init__(self, screen, map):
        self.screen = screen
        self.current_direction = 'stopped'
        self.map = map

        self.x = PACMAN_GRID_SIZE * 9 + PACMAN_X_OFFSET
        self.y = PACMAN_GRID_SIZE * 9 + PACMAN_Y_OFFSET

    def draw(self, pacman_powered_up=False):
        if pacman_powered_up:
            pygame.draw.rect(self.screen, (0, 255, 0), (self.x, self.y, PACMAN_GRID_SIZE, PACMAN_GRID_SIZE))
        else:
            pygame.draw.rect(self.screen, (255, 0, 0), (self.x, self.y, PACMAN_GRID_SIZE, PACMAN_GRID_SIZE))

    def get_possible_directions(self):
        possible_directions = []
        for direction in ['up', 'down', 'left', 'right']:
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

    def update(self, pacman_rect=None, pacman_powered_up=False):
        if pacman_rect:
            self.move_towards_pacman(pacman_rect)
        else:
            self.move_randomly()

    def move_randomly(self):
        possible_directions = self.get_possible_directions()
        if possible_directions:
            self.current_direction = random.choice(possible_directions)
            self.move()
    
    def move_towards_pacman(self, pacman_rect):
        pacman_pos = self.map.get_pos(pacman_rect)
        ghost_pos = self.map.get_pos(pygame.Rect(self.x, self.y, PACMAN_GRID_SIZE, PACMAN_GRID_SIZE))
        next_move = self.breadth_first_search(ghost_pos, pacman_pos)
        if next_move[0] > ghost_pos[0]:
            self.current_direction = 'right'
        if next_move[0] < ghost_pos[0]:
            self.current_direction = 'left'
        if next_move[1] > ghost_pos[1]:
            self.current_direction = 'down'
        if next_move[1] < ghost_pos[1]:
            self.current_direction = 'up'
        self.move()

    def move(self):
        if self.current_direction == 'up':
            self.y -= GHOST_VEL
        if self.current_direction == 'down':
            self.y += GHOST_VEL
        if self.current_direction == 'left':
            self.x -= GHOST_VEL
        if self.current_direction == 'right':
            self.x += GHOST_VEL

    def breadth_first_search(self, start, end):
        '''Returns the first move of the shortest path'''
        queue = [start]
        visited = set()
        visited.add(start)
        parent = {}

        while queue:
            current = queue.pop(0)

            if current == end:
                break

            for direction in ['up', 'down', 'left', 'right']:
                if queue == []:
                    if not self.can_move(direction):
                        continue

                x, y = current
                if direction == 'up':
                    new = (x, y - 1)
                if direction == 'down':
                    new = (x, y + 1)
                if direction == 'left':
                    new = (x - 1, y)
                if direction == 'right':
                    new = (x + 1, y)
                

                if new not in visited and not map_grid[new[0]][new[1]] == 1:
                    queue.append(new)
                    visited.add(new)
                    parent[new] = current

        # get the first move
        current = end
        while parent[current] != start:
            current = parent[current]

        return current