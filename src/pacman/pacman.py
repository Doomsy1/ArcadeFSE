import pygame
from src.pacman.ghost import Ghost
from src.pacman.map import PacmanMap
from src.pacman.player import PacmanPlayer
from utils import write_centered_text

# Constants
FPS = 60

class PacmanGame:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        self.map = PacmanMap(screen)

        self.player = PacmanPlayer(screen, self.map)

        self.ghosts = []
        for ghost_type in ['blinky', 'pinky', 'inky', 'clyde']:
            self.ghosts.append(Ghost(screen, self.map, self.player, ghost_type))

    def handle_ghost_collision(self):
        for ghost in self.ghosts:
            if self.player.rect.colliderect(ghost.rect):
                if ghost.fear_timer > 0:
                    ghost.reset()
                    self.player.score += 200 # TODO: add scaling for multiple ghosts
                else:
                    self.player.reset()
                    for ghost in self.ghosts:
                        ghost.reset()
                    return

    def new_level(self):
        self.map = PacmanMap(self.screen)

        score = self.player.score
        self.player = PacmanPlayer(self.screen, self.map, score=score)

        self.ghosts = []
        for ghost_type in ['blinky', 'pinky', 'inky', 'clyde']:
            self.ghosts.append(Ghost(self.screen, self.map, self.player, ghost_type))

        # add animation for new level
        while True:
            break # TODO: animation

    def draw_ui(self):
        # draw score
        score_rect = pygame.Rect(0, 0, 100, 50)
        pygame.draw.rect(self.screen, (0, 0, 0), score_rect)
        score_text = f'Score: {self.player.score}'
        write_centered_text(self.screen, score_text, score_rect, (255, 255, 255))

        # draw level TODO
        # level_rect = pygame.Rect(200, 0, 100, 50)
        # pygame.draw.rect(self.screen, (0, 0, 0), level_rect)
        # level_text = f'Level: {self.map.level}'
        # write_centered_text(self.screen, level_text, level_rect, (255, 255, 255))


    def main_loop(self):
        running = True
        while running:
            # handle events
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    return 'main menu'
                # escape key
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return 'main menu'
            
            self.mx, self.my = pygame.mouse.get_pos()

            if self.map.is_level_complete():
                self.new_level()
            
            self.map.draw()
            self.player.handle_keys(events)
            self.player.update()
            self.player.draw()

            for ghost in self.ghosts:
                ghost.update()
                ghost.draw()
            
            self.player.powered_up = False

            self.handle_ghost_collision()

            self.draw_ui()

            cur_fps = FPS + self.player.score // 250
            # set the caption as the fps
            pygame.display.set_caption(f'Pacman | FPS: {int(self.clock.get_fps())}')
            self.clock.tick(cur_fps)
            print(cur_fps)
            pygame.display.flip()
        return 'exit'