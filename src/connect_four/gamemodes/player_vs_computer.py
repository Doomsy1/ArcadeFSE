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

class Piece:
    def __init__(self, x, desired_y, color):
        self.x = x
        self.y = CONNECT_FOUR_Y_OFFSET - CONNECT_FOUR_RADIUS
        self.color = color

        self.desired_y = desired_y
        self.y_velocity = 0

    def update(self):
        if self.y == self.desired_y and self.y_velocity == 0:
            return

        if self.y + self.y_velocity > self.desired_y:
            self.y_velocity*= -ENERGY_RETAINED # flip the velocity and lose some energy

        self.y_velocity += GRAVITY_ACCELERATION

        self.y += self.y_velocity
        
        if self.desired_y - self.y < STOP_BOUNCING_THRESHOLD and self.y_velocity < STOP_BOUNCING_THRESHOLD:
            self.y = self.desired_y
            self.y_velocity = 0

    def draw(self, screen: pygame.Surface):
        pygame.draw.circle(screen, self.color, (self.x, self.y), CONNECT_FOUR_RADIUS)

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
        self.screen.blit(self.board_image, (CONNECT_FOUR_X_OFFSET, CONNECT_FOUR_Y_OFFSET))

    def update_pieces(self):
        for piece in self.pieces:
            piece.update()

    def draw_pieces(self):
        for piece in self.pieces:
            piece.draw(self.screen)

    def drop_piece(self, col):
        if self.human_turn:
            if self.board.is_valid_move(col):

                row = self.board.get_row(col)
                self.board.drop_piece(col)

                self.engine.update_board(self.board)
                self.result_container = []
                threading.Thread(target=self.engine.iterative_deepening, args=(self.result_container,)).start()

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
        if not self.result_container:
            return
        if self.result_container[-1][1]:
            col = self.result_container[-1][0]
            row = self.board.get_row(col)
            self.board.drop_piece(col)

            x = CONNECT_FOUR_X_OFFSET + col * CONNECT_FOUR_GRID_SIZE + CONNECT_FOUR_GRID_SIZE // 2
            desired_y = CONNECT_FOUR_Y_OFFSET + (5 - row) * CONNECT_FOUR_GRID_SIZE + CONNECT_FOUR_GRID_SIZE // 2
            piece = Piece(x, desired_y, (0, 255, 0))
            self.pieces.append(piece)
            self.human_turn = True

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return "exit"
            # escape key
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    return "exit"

            if event.type == pygame.MOUSEBUTTONDOWN:
                col = (event.pos[0] - CONNECT_FOUR_X_OFFSET) // CONNECT_FOUR_GRID_SIZE
                self.drop_piece(col)

    def main_loop(self):
        running = True

        while running:
            self.handle_input()

            if not self.human_turn:
                self.request_engine_move()

            # draw
            self.draw()

            winner = self.board.check_winner()
            if winner:
                text = f"Player {winner} wins!"
                winner_rect = pygame.Rect(0, 0, 200, 50)
                # draw background
                pygame.draw.rect(self.screen, (255, 255, 255), winner_rect)
                # draw text
                write_centered_text(self.screen, text, winner_rect, (0, 0, 0))

            pygame.display.flip()
            pygame.time.Clock().tick(FPS)

        return "connect four main menu"