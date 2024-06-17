# constants for the chess game
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)

SELECTED_SQUARE_COLOR = (0, 255, 0)
SELECTED_SQUARE_ALPHA = 100

MOVE_SQUARE_COLOR = (255, 165, 0)
MOVE_SQUARE_ALPHA = 100

CAPTURE_SQUARE_COLOR = (255, 0, 0)
CAPTURE_SQUARE_ALPHA = 100

# board
BOARD_OFFSET_X, BOARD_OFFSET_Y = 100, 200
CHESS_GRID_SIZE = 75

# annotation
CIRCLE_COLOR = (200, 130, 0)
CIRCLE_ALPHA = 196
CIRCLE_THICKNESS = 4

ARROW_COLOR = (255, 165, 0)
ARROW_ALPHA = 196
ARROW_TAIL_START_OFFSET = CHESS_GRID_SIZE // 4
TAIL_WIDTH = CHESS_GRID_SIZE // 4
HEAD_WIDTH = CHESS_GRID_SIZE // 2
HEAD_HEIGHT = CHESS_GRID_SIZE // 2.5

ENGINE_SUGGESTION_COLOR = (0, 0, 255)
ENGINE_SUGGESTION_ALPHA = 100

PREVIOUS_MOVE_COLOR = (50, 50, 100)
PREVIOUS_MOVE_ALPHA = 128


# constants for the pacman game
PACMAN_VEL = 5  # velocity of Pac-Man

PACMAN_X_OFFSET, PACMAN_Y_OFFSET = 0, 160
PACMAN_GRID_SIZE = 40

GHOST_VEL = 2  # velocity of the ghosts



# constants for the connect four game
BOARD_COLOR = (0, 0, 255)
TRANSPARENT_COLOR = (0, 0, 0, 0)

CONNECT_FOUR_GRID_SIZE = 109
CONNECT_FOUR_RADIUS = 40

CONNECT_FOUR_X_OFFSET, CONNECT_FOUR_Y_OFFSET = -2, 350