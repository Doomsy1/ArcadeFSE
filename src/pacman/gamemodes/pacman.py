import datetime
import pygame
import json
from tkinter import simpledialog
import tkinter as tk
from src.pacman.ghost import Ghost
from src.pacman.map import PacmanMap
from src.pacman.player import PacmanPlayer
from utils import write_centered_text

# Constants
FPS = 60

class Pacman:
    def __init__(self, screen):
        self.screen = screen
        self.clock = pygame.time.Clock()

        self.root = tk.Tk()
        self.root.withdraw()

        self.map = PacmanMap(screen)

        self.player = PacmanPlayer(screen, self.map)

        self.ghosts = []
        for ghost_type in ['blinky', 'pinky', 'inky', 'clyde']:
            self.ghosts.append(Ghost(screen, self.map, self.player, ghost_type))

        self.lives = 3

    def eating_ghost_animation(self, ghost):
        pass # TODO: animation for eating ghost (flashing ghost, score, etc.)

    def dying_animation(self):
        # TODO: add full death animation

        # clear ghosts
        for ghost in self.ghosts:
            ghost.reset() 

        tick = 60
        while tick > 0:
            tick -= 1

            # draw pacman with open mouth
            self.map.draw()
            
            frame = tick // 20
            self.player.draw_death(frame)

            pygame.display.flip()
            self.clock.tick(60)

        self.lives -= 1
        if self.lives == 0:
            self.draw_game_over()
            return 'game over'
        else:
            self.player.reset()
            return 'continue'

    def draw_game_over(self):
        tick = 60
        while tick > 0:
            tick -= 1

            # draw game over screen
            game_over_rect = pygame.Rect(0, 0, self.screen.get_width(), self.screen.get_height())
            game_over_text = 'Game Over'
            game_over_color =  (255, 0, 0)
            write_centered_text(self.screen, game_over_text, game_over_rect, game_over_color)

            pygame.display.flip()
            self.clock.tick(60)

    def handle_ghost_collision(self):
        for ghost in self.ghosts:
            if self.player.rect.colliderect(ghost.rect):
                if ghost.fear_timer > 0:
                    ghost.reset()
                    self.player.score += 200 # TODO: add scaling for multiple ghosts
                else:
                    return self.dying_animation()
                
        return 'continue'

    def add_leaderboard_entry(self):
        user = simpledialog.askstring('Leaderboard', 'Enter your name:').title()
        if user is None:
            return

        current_time = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        score = self.player.score


        with open('src\pacman\leaderboard.json', 'r') as f:
            leaderboard = json.load(f)

        if user not in leaderboard:
            previous_highscore = 0
            leaderboard[user] = []
        else:
            previous_highscore = max([score for _, score in leaderboard[user]])

        if score > previous_highscore:
            self.new_highscore()

        leaderboard[user].append((current_time, score))
        
        with open('src\pacman\leaderboard.json', 'w') as f:
            json.dump(leaderboard, f)
        
    def new_highscore(self):
        # write new highscore
        tick = 60
        while tick > 0:
            tick -= 1

            text = 'New Personal Best!'
            color = (255, 165, 0)
            rect = pygame.Rect(0, 0, self.screen.get_width(), self.screen.get_height()//5)

            write_centered_text(self.screen, text, rect, color)

            pygame.display.flip()
            self.clock.tick(60)

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
                    return 'pacman main menu'
                # escape key
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return 'pacman main menu'
            
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

            # ghost collision
            result = self.handle_ghost_collision()
            if result == 'game over':
                self.add_leaderboard_entry()
                return 'pacman main menu'
            elif result == 'continue':
                pass

            self.draw_ui()

            cur_fps = FPS + self.player.score // 250
            # set the caption as the fps
            pygame.display.set_caption(f'Pacman | FPS: {int(self.clock.get_fps())}')
            self.clock.tick(cur_fps)
            pygame.display.flip()
        return 'exit'