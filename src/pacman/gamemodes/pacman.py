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

        # hide the root window
        self.root = tk.Tk()
        self.root.withdraw()

        # load map
        self.map = PacmanMap(screen)

        # load player
        self.player = PacmanPlayer(screen, self.map)

        # load ghosts
        self.ghosts = []
        for ghost_type in ['blinky', 'pinky', 'inky', 'clyde']:
            self.ghosts.append(Ghost(screen, self.map, self.player, ghost_type))

        self.lives = 3
        self.level = 1

        self.load_highscore()

        self.load_images()

        self.load_sfx()

        self.start_animation()

    def load_highscore(self):
        with open('src\pacman\leaderboard.json', 'r') as f:
            leaderboard = json.load(f)

        highscore = 0
        for user in leaderboard:
            user_highscore = max([score for _, score in leaderboard[user]])
            highscore = max(highscore, user_highscore)

        self.highscore = highscore

    def load_images(self):
        self.images = {}
        life = pygame.image.load('src\pacman\\assets\misc\life.png')
        # scale to be 50x50
        life = pygame.transform.scale(life, (50, 50))
        self.images['life'] = life

    def load_sfx(self):
        pygame.mixer.init()

        self.sfx = {}
        self.sfx['eat'] = pygame.mixer.Sound('src\pacman\\assets\sfx\chomp.mp3')
        self.sfx['eat_ghost'] = pygame.mixer.Sound('src\pacman\\assets\sfx\eating_ghost.mp3')
        self.sfx['death'] = pygame.mixer.Sound('src\pacman\\assets\sfx\death.mp3')
        self.sfx['retreat'] = pygame.mixer.Sound('src\pacman\\assets\sfx\\retreating.mp3')
        self.sfx['siren'] = pygame.mixer.Sound('src\pacman\\assets\sfx\siren.mp3')
        self.sfx['start'] = pygame.mixer.Sound('src\pacman\\assets\sfx\start.mp3')

        # set volume
        for sound in self.sfx:
            self.sfx[sound].set_volume(0.1)

    def start_animation(self):
        # reset background
        self.screen.fill((0, 0, 0))

        # play start sound
        self.sfx['start'].play()

        # draw basic things
        self.draw_game()

        tick = 270
        while tick > 0:
            tick -= 1

            pygame.display.flip()
            self.clock.tick(60)

    def dying_animation(self):
        # play death sound
        self.sfx['death'].play()
        self.lives -= 1

        tick = 90
        while tick > 0:
            tick -= 1

            # draw basic things (not including player)
            self.map.draw()
            self.draw_ui()
            for ghost in self.ghosts:
                ghost.draw()
            
            frame = tick // 30
            self.player.draw_death(frame)

            pygame.display.flip()
            self.clock.tick(60)

        # clear ghosts
        for ghost in self.ghosts:
            ghost.reset() 

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

    def eat_ghost(self, ghost):
        # play sound effect
        self.sfx['eat_ghost'].play()

        # draw score above the ghost
        g_rect = ghost.rect
        score_rect = pygame.Rect(g_rect.centerx - 25, g_rect.centery - 25, 50, 50)
        
        # reset ghost
        ghost.reset()

        # calculate score (200, 400, 800, 1600)
        feared_ghosts = 0
        for ghost in self.ghosts:
            if ghost.fear_timer > 0:
                feared_ghosts += 1

        bonus = 200 * 2 ** (3 - feared_ghosts)
        score_text = str(bonus)
        self.player.score += bonus
        
        tick = 30
        while tick > 0:
            tick -= 1

            # draw basic things
            self.draw_game()

            write_centered_text(self.screen, score_text, score_rect, (255, 255, 255))

            pygame.display.flip()
            self.clock.tick(60)
        
    def handle_ghost_collision(self):
        for ghost in self.ghosts:
            if self.player.rect.colliderect(ghost.rect):
                if ghost.fear_timer > 0:
                    self.eat_ghost(ghost)
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
            previous_best = 0
            leaderboard[user] = []
        else:
            previous_best = max([score for _, score in leaderboard[user]])

        if score > previous_best:
            if score > self.highscore:
                self.new_personal_best(highscore=True)
            else:
                self.new_personal_best()

        leaderboard[user].append((current_time, score))
        
        with open('src\pacman\leaderboard.json', 'w') as f:
            json.dump(leaderboard, f)
        
    def new_personal_best(self, highscore=False):
        # write new highscore
        tick = 60
        while tick > 0:
            tick -= 1

            if highscore: # new highscore
                text = 'New Highscore!'
            else: # new personal best
                text = 'New Personal Best!'

            color = (255, 165, 0)
            rect = pygame.Rect(0, 0, self.screen.get_width(), self.screen.get_height()//5)

            # clear background
            self.screen.fill((0, 0, 0))

            # draw basic things
            self.map.draw()
            self.player.draw()
            for ghost in self.ghosts:
                ghost.draw()

            write_centered_text(self.screen, text, rect, color)

            pygame.display.flip()
            self.clock.tick(60)

    def new_level(self):
        self.level += 1

        # play start sound
        self.sfx['start'].play()

        self.map = PacmanMap(self.screen)

        score = self.player.score
        self.player = PacmanPlayer(self.screen, self.map, score=score)

        self.ghosts = []
        for ghost_type in ['blinky', 'pinky', 'inky', 'clyde']:
            self.ghosts.append(Ghost(self.screen, self.map, self.player, ghost_type))

        # add animation for new level
        tick = 270
        while tick > 0:
            tick -= 1

            # draw basic things
            self.draw_game()

            pygame.display.flip()
            self.clock.tick(60)

    def draw_ui(self):
        # draw score
        score_rect = pygame.Rect(0, 125, 200, 25)
        score_text = f'Score: {self.player.score}'
        write_centered_text(self.screen, score_text, score_rect, (255, 255, 255))

        # draw lives
        for i in range(self.lives):
            life_rect = pygame.Rect(self.screen.get_width() - 50 * (i + 1), 100, 50, 50)
            self.screen.blit(self.images['life'], life_rect)

        # draw highscore (top center)
        highscore_width = 400
        highscore_height = 100
        highscore_rect = pygame.Rect(self.screen.get_width()//2 - highscore_width//2, 0, highscore_width, highscore_height)
        highscore_text = f'Highscore: {self.highscore}'
        write_centered_text(self.screen, highscore_text, highscore_rect, (255, 255, 255))

        # draw level (centered below highscore)
        level_width = 200
        level_height = 50
        level_rect = pygame.Rect(self.screen.get_width()//2 - level_width//2, highscore_height, level_width, level_height)
        level_text = f'Level {self.level}'
        write_centered_text(self.screen, level_text, level_rect, (255, 255, 255))

    def play_ghost_siren(self):
        return
    
        # if there are any fearred ghosts, play the fearred ghost sound, otherwise play the siren sound
        feared = False
        for ghost in self.ghosts:
            if ghost.fear_timer > 0:
                feared = True
                break
        
        if feared:
            self.sfx['retreat'].play()
        else:
            self.sfx['siren'].play()
            

    def draw_game(self):
        # reset background
        self.screen.fill((0, 0, 0))

        # draw basic things
        self.map.draw()
        self.player.draw()
        self.draw_ui()
        for ghost in self.ghosts:
            ghost.draw()

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
            
            # reset background
            self.screen.fill((0, 0, 0))

            self.mx, self.my = pygame.mouse.get_pos()

            if self.map.is_level_complete():
                self.new_level()
            
            self.map.draw()
            self.player.handle_keys(events)
            pellet_eaten = self.player.update()
            # TODO: play sound effect for eating pellet
            # if pellet_eaten and not self.eat_channel.get_busy():
            #     self.eat_channel.play(self.sfx['eat'])
            self.player.draw()

            self.play_ghost_siren()

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