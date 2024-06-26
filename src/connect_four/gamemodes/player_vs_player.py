from src.connect_four.board import Board
import pygame
from constants import BOARD_COLOR, TRANSPARENT_COLOR, CONNECT_FOUR_GRID_SIZE, CONNECT_FOUR_RADIUS, CONNECT_FOUR_X_OFFSET, CONNECT_FOUR_Y_OFFSET
from utils import write_centered_text, Button

GRAVITY_ACCELERATION = 5
ENERGY_RETAINED = 0.75
STOP_BOUNCING_THRESHOLD = 5

FPS = 60

pygame.mixer.init()
drop_sound = pygame.mixer.Sound('src\connect_four\\assets\coin_drop.mp3')

back_button = {
    'text': 'Back',
    'rect': pygame.Rect(0, 0, 150, 50),
    'action': 'connect four main menu',
    'base_color': (0, 206, 209),
    'hover_color': (64, 224, 208),
    'clicked_color': (0, 139, 139),
    'text_color': (255, 255, 255),
    'description': 'Return to the main menu'
}

class Piece:
    def __init__(self, x, desired_y, color):
        self.x = x
        self.y = CONNECT_FOUR_Y_OFFSET - CONNECT_FOUR_RADIUS
        self.bg_color = color
        self.detail_color = (color[0] // 2, color[1] // 2, color[2] // 2)

        self.desired_y = desired_y
        self.y_velocity = 0

        # play sound
        drop_sound.play()

    def update(self):
        # if the piece is at the desired y position and has no velocity, return
        if self.y == self.desired_y and self.y_velocity == 0:
            return

        # if the piece is stil above the desired y position, move it down
        if self.y + self.y_velocity > self.desired_y:
            self.y_velocity*= -ENERGY_RETAINED

        self.y_velocity += GRAVITY_ACCELERATION

        self.y += self.y_velocity
        
        # if the piece is not moving and is close to the desired y position, stop it
        if self.desired_y - self.y < STOP_BOUNCING_THRESHOLD and abs(self.y_velocity) < STOP_BOUNCING_THRESHOLD:
            self.y = self.desired_y
            self.y_velocity = 0

    def draw(self, screen: pygame.Surface):
        # draw light circle
        pygame.draw.circle(screen, self.bg_color, (self.x, self.y), CONNECT_FOUR_RADIUS)

        # draw dark circles to give the piece a 3D effect
        # one on the inside
        pygame.draw.circle(screen, self.detail_color, (self.x, self.y), CONNECT_FOUR_RADIUS - 20)

        # one on the rim
        pygame.draw.circle(screen, self.detail_color, (self.x, self.y), CONNECT_FOUR_RADIUS, 5)
        

class PlayerVsPlayer:
    def __init__(self, screen):
        self.screen = screen
        self.board = Board()

        self.pieces = []

        self.turn = 1

        self.end_counter = 0

        self.board_image = self.create_board_image()

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

    def create_board_image(self):
        '''Create an image of the board'''
        # 7 columns, 6 rows
        # rectangle with 42 empty circles (transparent)

        board_image = pygame.Surface((CONNECT_FOUR_GRID_SIZE * 7, CONNECT_FOUR_GRID_SIZE * 6), pygame.SRCALPHA)
        board_image.fill(TRANSPARENT_COLOR)

        # draw the board
        board_image.fill(BOARD_COLOR)

        # draw circles
        for col in range(7):
            for row in range(6):
                x = col * CONNECT_FOUR_GRID_SIZE + CONNECT_FOUR_GRID_SIZE // 2
                y = row * CONNECT_FOUR_GRID_SIZE + CONNECT_FOUR_GRID_SIZE // 2
                pygame.draw.circle(board_image, TRANSPARENT_COLOR, (x, y), CONNECT_FOUR_RADIUS)

        return board_image

    def draw_board(self):
        '''Draw the board on the screen'''
        self.screen.blit(self.board_image, (CONNECT_FOUR_X_OFFSET, CONNECT_FOUR_Y_OFFSET))

    def update_pieces(self):
        '''Update the pieces on the board'''
        for piece in self.pieces:
            piece.update()

    def draw_pieces(self):
        '''Draw the pieces on the screen'''
        for piece in self.pieces:
            piece.draw(self.screen)

    def drop_piece(self, col):
        '''Drop a piece in the specified column'''
        if self.end_counter > 0:
            return
        
        if self.board.is_valid_move(col):
            
            row = self.board.get_row(col)
            self.board.drop_piece(col)

            # drop the piece
            x = CONNECT_FOUR_X_OFFSET + col * CONNECT_FOUR_GRID_SIZE + CONNECT_FOUR_GRID_SIZE // 2
            desired_y = CONNECT_FOUR_Y_OFFSET + (5 - row) * CONNECT_FOUR_GRID_SIZE + CONNECT_FOUR_GRID_SIZE // 2
            piece_color = (255, 0, 0) if self.turn == 1 else (0, 255, 0)
            piece = Piece(x, desired_y, piece_color)
            self.pieces.append(piece)

            self.turn = 1 if self.turn == 2 else 2



    def draw_background(self):
        self.screen.fill((32, 32, 32))

    def draw_game(self):
        self.draw_background()

        self.update_pieces()
        self.draw_pieces()

        self.draw_board()

    def handle_events(self):
        self.mx, self.my = pygame.mouse.get_pos()
        self.L_mouse_up = False
        self.mb = pygame.mouse.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'connect four main menu'
            # escape key
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'connect four main menu'
            if event.type == pygame.MOUSEBUTTONUP:
                self.L_mouse_up = True
                    

            if event.type == pygame.MOUSEBUTTONDOWN:
                col = (event.pos[0] - CONNECT_FOUR_X_OFFSET) // CONNECT_FOUR_GRID_SIZE
                self.drop_piece(col)

    def main_loop(self):
        running = True

        while running:
            menu_change = self.handle_events()
            if menu_change:
                return menu_change

            # draw
            self.draw_game()

            # draw the back button
            self.back_button.draw(self.mx, self.my, self.mb)

            # check if the back button is clicked
            action = self.back_button.check_click(self.mx, self.my, self.L_mouse_up)
            if action:
                return action

            winner = self.board.check_winner()
            tie = self.board.is_full()
            if winner or tie:
                self.end_counter += 1
                if winner:
                    text = f'Player {winner} wins!'
                else:
                    text = 'It\'s a tie!'
                winner_rect = pygame.Rect(0, 0, 760, 300)
                # draw text
                write_centered_text(self.screen, text, winner_rect, (196, 196, 196))

                while self.end_counter > 120:
                    end_text = 'click to return to the menu'
                    end_rect = pygame.Rect(0, 225, 760, 100)
                    write_centered_text(self.screen, end_text, end_rect, (196, 64, 64))

                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            return 'connect four main menu'
                        if event.type == pygame.KEYDOWN:
                            return 'connect four main menu'
                        if event.type == pygame.MOUSEBUTTONUP:
                            return 'connect four main menu'

                        
                    pygame.display.flip()
                    pygame.time.Clock().tick(FPS)

            pygame.display.flip()
            pygame.time.Clock().tick(FPS)

        return 'connect four main menu'