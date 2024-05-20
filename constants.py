# Constants for the chess game
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
BOARD_OFFSET_X, BOARD_OFFSET_Y = 0, 0
CHESS_GRID_SIZE = 100

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


# Constants for the pacman game
GRID_SIZE = 32

VEL = 5  # Velocity of Pac-Man