import threading
from src.connect_four.board import Board
from src.connect_four.engine import Engine
import pygame
from constants import BOARD_COLOR, TRANSPARENT_COLOR, CONNECT_FOUR_GRID_SIZE, CONNECT_FOUR_RADIUS, CONNECT_FOUR_X_OFFSET, CONNECT_FOUR_Y_OFFSET
from utils import write_centered_text

GRAVITY_ACCELERATION = 5
ENERGY_RETAINED = 0.75
STOP_BOUNCING_THRESHOLD = 5

FPS = 60

pygame.mixer.init()
drop_sound = pygame.mixer.Sound('src\connect_four\\assets\coin_drop.mp3')

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
        

class PlayerVsComputer:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.board = Board()
        self.engine = Engine(self.board, time_limit_ms=1000)

        self.pieces = []

        self.board_image = self.create_board_image()

        self.result_container = []
        self.human_turn = True

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
        if self.human_turn:
            if self.board.is_valid_move(col):
                

                row = self.board.get_row(col)
                self.board.drop_piece(col)

                # update the board
                self.engine.update_board(self.board)
                self.result_container = []
                threading.Thread(target=self.engine.iterative_deepening, args=(self.result_container,)).start()

                # drop the piece
                x = CONNECT_FOUR_X_OFFSET + col * CONNECT_FOUR_GRID_SIZE + CONNECT_FOUR_GRID_SIZE // 2
                desired_y = CONNECT_FOUR_Y_OFFSET + (5 - row) * CONNECT_FOUR_GRID_SIZE + CONNECT_FOUR_GRID_SIZE // 2
                piece = Piece(x, desired_y, (255, 0, 0))
                self.pieces.append(piece)
                self.human_turn = False



    def draw_background(self):
        self.screen.fill((0, 0, 0))

    def draw(self):
        self.draw_background()

        self.update_pieces()
        self.draw_pieces()

        self.draw_board()

    def request_engine_move(self):
        # if the engine has not made a move yet, return
        if not self.result_container:
            return
        # if the engine has made a move
        if self.result_container[-1][1]:
            col = self.result_container[-1][0]
            row = self.board.get_row(col)
            self.board.drop_piece(col)

            # drop the piece
            x = CONNECT_FOUR_X_OFFSET + col * CONNECT_FOUR_GRID_SIZE + CONNECT_FOUR_GRID_SIZE // 2
            desired_y = CONNECT_FOUR_Y_OFFSET + (5 - row) * CONNECT_FOUR_GRID_SIZE + CONNECT_FOUR_GRID_SIZE // 2
            piece = Piece(x, desired_y, (0, 255, 0))
            self.pieces.append(piece)
            self.human_turn = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'connect four main menu'
            # escape key
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return 'connect four main menu'

            if event.type == pygame.MOUSEBUTTONDOWN:
                col = (event.pos[0] - CONNECT_FOUR_X_OFFSET) // CONNECT_FOUR_GRID_SIZE
                self.drop_piece(col)

    def main_loop(self):
        running = True

        while running:
            menu_change = self.handle_events()
            if menu_change:
                return menu_change

            if not self.human_turn:
                self.request_engine_move()

            # draw
            self.draw()

            winner = self.board.check_winner()
            if winner:
                text = f'Player {winner} wins!'
                winner_rect = pygame.Rect(0, 0, 200, 50)
                # draw background
                pygame.draw.rect(self.screen, (255, 255, 255), winner_rect)
                # draw text
                write_centered_text(self.screen, text, winner_rect, (0, 0, 0))

            pygame.display.flip()
            pygame.time.Clock().tick(FPS)

        return 'connect four main menu'