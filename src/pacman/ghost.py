import random
from constants import PACMAN_GRID_SIZE, PACMAN_X_OFFSET, PACMAN_Y_OFFSET, GHOST_VEL
import pygame

START_POS = {
    "blinky": (9, 8),
    "pinky": (9, 9),
    "inky": (8, 9),
    "clyde": (10, 9)
}
START_TICK = {
    "blinky": 0,
    "pinky": 100,
    "inky": 200,
    "clyde": 300
}
class Ghost:
    def __init__(self, screen, map, pacman, ghost_type): # TODO: add color to differentiate ghosts
        self.screen = screen
        self.current_direction = 'stopped'
        self.map = map
        self.ghost_type = ghost_type

        self.x = START_POS[self.ghost_type][0] * PACMAN_GRID_SIZE + PACMAN_X_OFFSET
        self.y = START_POS[self.ghost_type][1] * PACMAN_GRID_SIZE + PACMAN_Y_OFFSET

        self.tick = 0

        self.pacman = pacman

        self.rect = pygame.Rect(self.x, self.y, PACMAN_GRID_SIZE, PACMAN_GRID_SIZE)

    def reset(self):
        self.x = START_POS[self.ghost_type][0] * PACMAN_GRID_SIZE + PACMAN_X_OFFSET
        self.y = START_POS[self.ghost_type][1] * PACMAN_GRID_SIZE + PACMAN_Y_OFFSET
        self.current_direction = 'stopped'
        self.rect = pygame.Rect(self.x, self.y, PACMAN_GRID_SIZE, PACMAN_GRID_SIZE)

    def draw(self):
        if self.pacman.powered_up:
            if self.pacman.powered_up_timer % 12 < 4 and self.pacman.powered_up_timer < 250:
                pygame.draw.rect(self.screen, (255, 255, 255), (self.x, self.y, PACMAN_GRID_SIZE, PACMAN_GRID_SIZE))
            else:
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
        if direction == 'down' and self.map.is_gate(future_rect):
            return False
        
        return not self.map.is_wall(future_rect)

    def update(self):
        if self.tick < START_TICK[self.ghost_type]:
            self.tick += 1
            return
        if self.at_intersection():
            possible_directions = self.get_possible_directions()
            if len(possible_directions) == 1:
                self.current_direction = possible_directions[0]
                self.move()
                return

            best_direction = self.get_best_direction()
            if self.pacman.powered_up:
                # weigh the best direction lower than the others but still allow the ghost to move randomly
                if random.random() < 0.2: # 20% chance to move in the best direction
                    print(f"{self.ghost_type} moving in best direction")
                    self.current_direction = best_direction
                else: # 20% chance to move randomly (excluding the best direction)
                    print(f"{self.ghost_type} moving randomly")
                    if possible_directions:
                        if best_direction in possible_directions:
                            possible_directions.remove(best_direction)
                        self.current_direction = random.choice(possible_directions)
            else:
                # weigh the best direction higher than the others but still allow the ghost to move randomly
                if random.random() < 0.8: # 80% chance to move in the best direction
                    print(f"{self.ghost_type} moving in best direction - not powered up")
                    self.current_direction = best_direction
                else: # 80% chance to move randomly (including the best direction)
                    print(f"{self.ghost_type} moving randomly - not powered up")
                    if possible_directions:
                        self.current_direction = random.choice(possible_directions)
                
        self.move()

    def get_best_direction(self):
        '''Use bfs to find the best direction to move in'''
        pacman_pos = self.map.get_pos(self.pacman.rect)
        current_x, current_y = self.map.get_pos(self.rect)

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

        # if the ghost goes off the screen, wrap around
        if self.x < PACMAN_X_OFFSET:
            self.x = PACMAN_X_OFFSET + 19 * PACMAN_GRID_SIZE - GHOST_VEL

        if self.x > PACMAN_X_OFFSET + 19 * PACMAN_GRID_SIZE:
            self.x = PACMAN_X_OFFSET + GHOST_VEL

        self.rect = pygame.Rect(self.x, self.y, PACMAN_GRID_SIZE, PACMAN_GRID_SIZE)