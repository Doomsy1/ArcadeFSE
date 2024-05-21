import json
import pygame
from utils import write_centered_text, Slider



    


save_button = pygame.Rect(550, 650, 200, 100)

dark_square_preview_rect = pygame.Rect(300, 400, 200, 200)
light_square_preview_rect = pygame.Rect(550, 400, 200, 200)

class ChessSettingsMenu:
    def __init__(self, screen):
        self.screen = screen

        self.init_sliders()

        self.sliders = []
        for slider in self.sliders_data:
            self.sliders.append(Slider(
                screen=self.screen,
                label=slider,
                x=self.sliders_data[slider]['x'],
                y=self.sliders_data[slider]['y'],
                width=self.sliders_data[slider]['width'],
                height=self.sliders_data[slider]['height'],
                min_value=self.sliders_data[slider]['min_value'],
                max_value=self.sliders_data[slider]['max_value'],
                initial_value=self.sliders_data[slider]['initial_value'],
                interval=self.sliders_data[slider]['interval']
            ))

    def init_sliders(self):
        # read settings.json
        with open('src\chess\settings.json', 'r') as file:
            settings = json.load(file)

        self.sliders_data = {
            'difficulty': {
                'x': 50,
                'y': 100,
                'width': 200,
                'height': 50,
                'min_value': 1,
                'max_value': 5,
                'initial_value': settings['difficulty'],
                'interval': 1
            },
            'volume': {
                'x': 50,
                'y': 200,
                'width': 200,
                'height': 50,
                'min_value': 0,
                'max_value': 100,
                'initial_value': settings['volume'],
                'interval': 5
            },
            'dark_square_color_r': {
                'x': 300,
                'y': 100,
                'width': 200,
                'height': 50,
                'min_value': 0,
                'max_value': 255,
                'initial_value': settings['dark_square_color']['r'],
                'interval': 5
            },
            'dark_square_color_g': {
                'x': 300,
                'y': 200,
                'width': 200,
                'height': 50,
                'min_value': 0,
                'max_value': 255,
                'initial_value': settings['dark_square_color']['g'],
                'interval': 5
            },
            'dark_square_color_b': {
                'x': 300,
                'y': 300,
                'width': 200,
                'height': 50,
                'min_value': 0,
                'max_value': 255,
                'initial_value': settings['dark_square_color']['b'],
                'interval': 5
            },
            'light_square_color_r': {
                'x': 550,
                'y': 100,
                'width': 200,
                'height': 50,
                'min_value': 0,
                'max_value': 255,
                'initial_value': settings['light_square_color']['r'],
                'interval': 5
            },
            'light_square_color_g': {
                'x': 550,
                'y': 200,
                'width': 200,
                'height': 50,
                'min_value': 0,
                'max_value': 255,
                'initial_value': settings['light_square_color']['g'],
                'interval': 5
            },
            'light_square_color_b': {
                'x': 550,
                'y': 300,
                'width': 200,
                'height': 50,
                'min_value': 0,
                'max_value': 255,
                'initial_value': settings['light_square_color']['b'],
                'interval': 5
            },
            'time_per_side': {
                'x': 50,
                'y': 300,
                'width': 200,
                'height': 50,
                'min_value': 15,
                'max_value': 300,
                'initial_value': settings['time_per_side'],
                'interval': 15
            },
            'time_increment': {
                'x': 50,
                'y': 400,
                'width': 200,
                'height': 50,
                'min_value': 0,
                'max_value': 15,
                'initial_value': settings['time_increment'],
                'interval': 1
            }
        }

    def update_sliders(self, mx, my, lmx, lmy):
        for slider in self.sliders:
            slider.draw()
            slider.update(mx, my, lmx, lmy)

    def save_settings(self):
        settings = {
            'difficulty': self.sliders[0].get_value(),
            'volume': self.sliders[1].get_value(),
            'dark_square_color': {
                'r': self.sliders[2].get_value(),
                'g': self.sliders[3].get_value(),
                'b': self.sliders[4].get_value()
            },
            'light_square_color': {
                'r': self.sliders[5].get_value(),
                'g': self.sliders[6].get_value(),
                'b': self.sliders[7].get_value()
            },
            'time_per_side': self.sliders[8].get_value(),
            'time_increment': self.sliders[9].get_value()
        }

        with open('src\chess\settings.json', 'w') as file:
            json.dump(settings, file)

    def update_save_button(self):
        pygame.draw.rect(self.screen, (255, 255, 255), save_button)
        if pygame.mouse.get_pressed()[0]:
            if save_button.collidepoint(self.mx, self.my) and save_button.collidepoint(self.lmx, self.lmy):
                pygame.draw.rect(self.screen, (64, 128, 64), save_button)
                self.save_settings()

        write_centered_text(self.screen, 'Save', save_button, (0, 0, 0))

    def draw_square_color_preview(self):
        dark_square_color = (
            self.sliders[2].get_value(), 
            self.sliders[3].get_value(), 
            self.sliders[4].get_value()
            )
        
        light_square_color = (
            self.sliders[5].get_value(), 
            self.sliders[6].get_value(), 
            self.sliders[7].get_value()
            )

        # draw the dark and light square preview
        pygame.draw.rect(self.screen, dark_square_color, dark_square_preview_rect)
        pygame.draw.rect(self.screen, light_square_color, light_square_preview_rect)
        
        # draw a border around the dark and light square preview
        pygame.draw.rect(self.screen, (0, 0, 0), dark_square_preview_rect, 5)
        pygame.draw.rect(self.screen, (0, 0, 0), light_square_preview_rect, 5)
        

    def main_loop(self):
        running = True

        self.lmx, self.lmy = pygame.mouse.get_pos()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                # if the player presses escape, return to the main menu
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return 'chess main menu'
                # if the player presses the left mouse button
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.lmx, self.lmy = pygame.mouse.get_pos()
                    
            self.mx, self.my = pygame.mouse.get_pos()

            self.screen.fill((128, 128, 128)) # replace this with a background image

            self.update_sliders(self.mx, self.my, self.lmx, self.lmy)

            # if the player clicks on the save button, save the settings
            self.update_save_button()
            
            self.draw_square_color_preview()

            pygame.display.flip()

        return 'chess main menu'