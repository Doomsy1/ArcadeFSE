import pygame
import numpy as np
import pygame.font as pygame_font

pygame_font.init()

class Slider:
    def __init__(self, screen, label, x, y, width, height, min_value, max_value, initial_value, interval):
        self.screen = screen
        self.label = label.replace('_', ' ').title()
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.min_value = min_value
        self.max_value = max_value
        self.value = initial_value

        self.interval = interval

        self.thumb_width = 10
        self.thumb_height = self.height + 10

    def draw(self):
        # background of the slider
        pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(self.x, self.y, self.width, self.height))

        # outline of the slider
        pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(self.x, self.y, self.width, self.height), 2)

        # slider track
        track_width = (self.value - self.min_value) * self.width / (self.max_value - self.min_value)
        pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(self.x, self.y, track_width, self.height))

        # slider thumb
        thumb_x = self.x + track_width - self.thumb_width // 2
        thumb_y = self.y - 5
        pygame.draw.rect(self.screen, (64, 64, 64), pygame.Rect(thumb_x, thumb_y, self.thumb_width, self.thumb_height))

        write_centered_text(self.screen, self.label, pygame.Rect(self.x+5, self.y+5, self.width-10, self.height-10), (255, 160, 0))

    def update(self, mx, my, lmx, lmy):
        if pygame.mouse.get_pressed()[0]:
            if pygame.Rect(self.x, self.y, self.width, self.height).collidepoint((lmx, lmy)):
                # update the value of the slider based on the mouse position
                self.value = (mx - self.x) * (self.max_value - self.min_value) / self.width + self.min_value
                self.value = max(self.min_value, min(self.max_value, self.value))
                self.value = round(self.value / self.interval) * self.interval

                # display the value of the slider with a label
                value_label_width, value_label_height = 50, 50
                value_label_x = self.x + self.width // 2 - value_label_width // 2
                value_label_y = self.y - value_label_height

                # draw the background of the value label
                pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(value_label_x, value_label_y, value_label_width, value_label_height))

                # draw the outline of the value label
                pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(value_label_x, value_label_y, value_label_width, value_label_height), 2)

                # write the value of the slider
                write_centered_text(self.screen, str(int(self.value)), pygame.Rect(value_label_x, value_label_y, value_label_width, value_label_height), (0, 0, 0))

    def get_value(self):
        return self.value

def draw_arrow(screen, start, end, tail_start_offset, tail_width, head_width, head_height, color, alpha, cache={}):
    # Check if the arrow has already been rendered with the same parameters
    key = (start, end, tail_start_offset, tail_width, head_width, head_height, color, alpha)
    if key in cache:
        screen.blit(cache[key], (0, 0))
        return

    # Vector from start to end
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = np.hypot(dx, dy)
    if length == 0:
        return  # Cannot draw an arrow if length is 0

    # Normalize the direction vector
    dx, dy = dx / length, dy / length

    # Calculate new start point for the tail with the offset
    tail_start_x = start[0] + dx * tail_start_offset
    tail_start_y = start[1] + dy * tail_start_offset

    # Perpendicular vector for width calculations
    perpx, perpy = -dy, dx

    # Adjusted end point for the tail to stop before the head starts
    tail_end_x = end[0] - dx * head_height
    tail_end_y = end[1] - dy * head_height

    # Points for the tail rectangle
    tail_rect_points = [
        (tail_start_x + perpx * tail_width / 2, tail_start_y + perpy * tail_width / 2),
        (tail_start_x - perpx * tail_width / 2, tail_start_y - perpy * tail_width / 2),
        (tail_end_x - perpx * tail_width / 2, tail_end_y - perpy * tail_width / 2),
        (tail_end_x + perpx * tail_width / 2, tail_end_y + perpy * tail_width / 2)
    ]

    # Points for the arrow head
    head_points = [
        (end[0], end[1]),
        (end[0] - perpx * head_width / 2 - dx * head_height, end[1] - perpy * head_width / 2 - dy * head_height),
        (end[0] + perpx * head_width / 2 - dx * head_height, end[1] + perpy * head_width / 2 - dy * head_height)
    ]

    # Create a temporary surface to draw the semi-transparent arrow
    temp_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    rgba_color = color + (alpha,)  # Adding the alpha value to the color tuple

    # Draw the tail rectangle with transparency
    pygame.draw.polygon(temp_surface, rgba_color, tail_rect_points)
    # Draw the head polygon with transparency
    pygame.draw.polygon(temp_surface, rgba_color, head_points)
    # Blit this surface onto the main screen surface
    screen.blit(temp_surface, (0, 0))

    # Cache the rendered arrow
    cache[key] = temp_surface.copy()

def draw_transparent_circle(screen, center, radius, color, alpha, cache={}):
    # Check if the circle has already been rendered with the same parameters
    key = (center, radius, color, alpha)
    if key in cache:
        screen.blit(cache[key], (0, 0))
        return

    # Create a temporary surface to handle transparency
    temp_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    rgba_color = color + (alpha,)  # Create RGBA color tuple

    # Draw the circle on the temporary surface
    pygame.draw.circle(temp_surface, rgba_color, center, radius)

    # Blit the temporary surface onto the main screen surface
    screen.blit(temp_surface, (0, 0))

    # Cache the rendered circle
    cache[key] = temp_surface.copy()

def write_centered_text(screen, text, rect, colour, cache={}):
    rect_tuple = (rect.x, rect.y, rect.width, rect.height) # Convert rect to a tuple
    key = (text, rect_tuple, colour) # Use the tuple as the key
    if key in cache: # If the text has already been rendered, use the cached version
        for text_surface, x, y in cache[key]:
            screen.blit(text_surface, (x, y))
        return

    # Split the text into lines and calculate the size of the text
    lines = text.split("\n")
    font_size = 1
    font_obj = pygame_font.Font(None, font_size)
    line_sizes = [(line, font_obj.size(line)) for line in lines]
    widest_line, widest_size = max(line_sizes, key=lambda item: item[1][0])
    text_height = sum(size[1] for _, size in line_sizes)
    text_width = widest_size[0]

    # binary search for the maximum font size
    low, high = font_size, max(rect.width, rect.height)
    while low < high:
        mid = (low + high + 1) // 2
        font_obj = pygame_font.Font(None, mid)
        line_sizes = [(line, font_obj.size(line)) for line in lines]
        text_height = sum(size[1] for _, size in line_sizes)
        text_width = max(size[0] for _, size in line_sizes)

        if text_height <= rect.height and text_width <= rect.width:
            low = mid
        else:
            high = mid - 1

    # Render the text with the maximum font size
    font_size = low
    font_obj = pygame_font.Font(None, font_size)
    line_sizes = [(line, font_obj.size(line)) for line in lines]
    text_height = sum(size[1] for _, size in line_sizes)
    text_width = max(size[0] for _, size in line_sizes)

    cache[key] = []
    y = rect.y + (rect.height - text_height) // 2
    for i, (line, size) in enumerate(line_sizes): # Render each line of text
        text_surface = font_obj.render(line, True, colour)
        x = rect.x + (rect.width - size[0]) // 2
        screen.blit(text_surface, (x, y + i * size[1]))

        # Cache the rendered text
        cache[key].append((text_surface, x, y + i * size[1]))

def draw_transparent_rect(screen, rect, color, alpha, thickness=0, cache={}):
    # Check if the rectangle has already been rendered with the same parameters
    key = (rect, color, alpha, thickness)
    if key in cache:
        screen.blit(cache[key], (0, 0))
        return

    # Create a temporary surface to handle transparency
    temp_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    rgba_color = color + (alpha,)  # Create RGBA color tuple

    # Draw the rectangle on the temporary surface
    pygame.draw.rect(temp_surface, rgba_color, rect, thickness)

    # Blit the temporary surface onto the main screen surface
    screen.blit(temp_surface, (0, 0))

    # Cache the rendered rectangle
    cache[key] = temp_surface.copy()