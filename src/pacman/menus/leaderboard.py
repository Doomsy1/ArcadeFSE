import pygame
import json
from utils import write_centered_text


class Leaderboard:
    def __init__(self, screen):
        self.screen = screen

        self.load_leaderboard()

        self.ordered_leaderboard = self.create_ordered_leaderboard()[:10]

    def load_leaderboard(self):
        with open('src\pacman\leaderboard.json', 'r') as f:
            self.leaderboard = json.load(f)

    def create_ordered_leaderboard(self):
        # name: (time, score)
        
        # get the max score of each player
        player_scores = []
        for player in self.leaderboard:
            player_time_scores = self.leaderboard[player]

            # sort the scores by score
            player_time_scores = sorted(player_time_scores, key=lambda x: x[1], reverse=True)
            
            # get the max time and score
            max_time, max_score = player_time_scores[0]

            player_scores.append((player, max_score, max_time))


        # sort the players by score
        ordered_leaderboard = sorted(player_scores, key=lambda x: x[1], reverse=True)
        
        return ordered_leaderboard
    
    def draw_leaderboard(self):
        
        leaderboard_header_rect = pygame.Rect(50, 50, 660, 100)
        write_centered_text(self.screen, 'Leaderboard', leaderboard_header_rect, (255, 160, 0))

        y = 150
        for i, (name, score, time) in enumerate(self.ordered_leaderboard):
            leaderboard_entry_rect = pygame.Rect(50, y, 660, 50)
            leaderboard_entry = f'{i+1}. {name}: {score}'
            write_centered_text(self.screen, leaderboard_entry, leaderboard_entry_rect, (255, 255, 255))
            y += 50

    def main_loop(self):
        running = True

        while running:
            self.screen.fill((0, 0, 0))
            self.draw_leaderboard()
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return 'pacman main menu'

        return 'exit'