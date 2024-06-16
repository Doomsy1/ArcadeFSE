import pygame
import json
from utils import Button, write_centered_text


back_button = {
    'text': 'Back',
    'rect': pygame.Rect(300, 880, 200, 100),
    'action': 'pacman main menu',
    'base_color': (0, 206, 209),
    'hover_color': (64, 224, 208),
    'clicked_color': (0, 139, 139),
    'text_color': (255, 255, 255),
    'description': 'Return to the main menu'
}

class Leaderboard:
    def __init__(self, screen):
        self.screen = screen

        self.load_leaderboard()

        self.ordered_leaderboard = self.create_ordered_leaderboard()[:10]

        self.load_background()

        self.back_button = Button(
            screen = self.screen,
            text = back_button['text'],
            rect = back_button['rect'],
            action = back_button['action'],
            base_color = back_button['base_color'],
            hover_color = back_button['hover_color'],
            clicked_color = back_button['clicked_color'],
            text_color = back_button['text_color'],
            descriptive_text = back_button['description']
        )

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
        
        leaderboard_header_rect = pygame.Rect(50, 50, 660, 150)

        # draw a black rect behind the header
        header_background_color = (25, 25, 112)
        pygame.draw.rect(self.screen, header_background_color, leaderboard_header_rect)

        # write the header
        write_centered_text(self.screen, 'Leaderboard', leaderboard_header_rect, (135, 206, 250))

        # draw the entries
        y = 200 # start y position
        entry_size = 60 # height of each entry
        for i, (name, score, time) in enumerate(self.ordered_leaderboard):
            leaderboard_entry_rect = pygame.Rect(50, y, 660, entry_size)
            leaderboard_entry = f'{i+1}. {name}: {score}'

            # alternate the background color
            if i % 2 == 0:
                background_color = (72, 61, 139)
                text_color = (255, 105, 180)
            else:
                background_color = (75, 0, 130)
                text_color = (0, 255, 255)

            # draw background
            pygame.draw.rect(self.screen, background_color, leaderboard_entry_rect)

            # write the entry
            write_centered_text(self.screen, leaderboard_entry, leaderboard_entry_rect, text_color)
            y += entry_size

    def load_background(self):
        background_path = "assets\LeaderboardBackground.png"

        self.background = pygame.image.load(background_path)

        # scale the image to fit the screen (760x1000)
        # scale to 1000x1000
        self.background = pygame.transform.scale(self.background, (1000, 1000))

    def draw_background(self):
        # center the background on the center of the screen
        screen_width, screen_height = self.screen.get_width(), self.screen.get_height()

        background_width, background_height = self.background.get_width(), self.background.get_height()

        x = (screen_width - background_width) / 2
        y = (screen_height - background_height) / 2

        self.screen.blit(self.background, (x, y))

    def main_loop(self):
        running = True

        while running:
            L_mouse_up = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "exit"
                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        L_mouse_up = True



            mx, my = pygame.mouse.get_pos()
            mb = pygame.mouse.get_pressed()

            # draw the background
            self.draw_background()

            # draw the leaderboard
            self.draw_leaderboard()

            # draw the back button
            self.back_button.draw(mx, my, mb)

            # check if the player clicked on the back button
            action = self.back_button.check_click(mx, my, L_mouse_up)
            if action:
                return action

            pygame.display.flip()

        return 'exit'