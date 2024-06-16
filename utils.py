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
    # check if the arrow has already been rendered with the same parameters
    key = (start, end, tail_start_offset, tail_width, head_width, head_height, color, alpha)
    if key in cache:
        screen.blit(cache[key], (0, 0))
        return

    # vector from start to end
    dx, dy = end[0] - start[0], end[1] - start[1]
    length = np.hypot(dx, dy)
    if length == 0:
        return  # Cannot draw an arrow if length is 0

    # normalize the direction vector
    dx, dy = dx / length, dy / length

    # calculate new start point for the tail with the offset
    tail_start_x = start[0] + dx * tail_start_offset
    tail_start_y = start[1] + dy * tail_start_offset

    # perpendicular vector for width calculations
    perpx, perpy = -dy, dx

    # adjusted end point for the tail to stop before the head starts
    tail_end_x = end[0] - dx * head_height
    tail_end_y = end[1] - dy * head_height

    # points for the tail rectangle
    tail_rect_points = [
        (tail_start_x + perpx * tail_width / 2, tail_start_y + perpy * tail_width / 2),
        (tail_start_x - perpx * tail_width / 2, tail_start_y - perpy * tail_width / 2),
        (tail_end_x - perpx * tail_width / 2, tail_end_y - perpy * tail_width / 2),
        (tail_end_x + perpx * tail_width / 2, tail_end_y + perpy * tail_width / 2)
    ]

    # points for the arrow head
    head_points = [
        (end[0], end[1]),
        (end[0] - perpx * head_width / 2 - dx * head_height, end[1] - perpy * head_width / 2 - dy * head_height),
        (end[0] + perpx * head_width / 2 - dx * head_height, end[1] + perpy * head_width / 2 - dy * head_height)
    ]

    # create a temporary surface to draw the semi-transparent arrow
    temp_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    rgba_color = color + (alpha,)  # Adding the alpha value to the color tuple

    # draw the tail rectangle with transparency
    pygame.draw.polygon(temp_surface, rgba_color, tail_rect_points)
    # draw the head polygon with transparency
    pygame.draw.polygon(temp_surface, rgba_color, head_points)
    # blit this surface onto the main screen surface
    screen.blit(temp_surface, (0, 0))

    # cache the rendered arrow
    cache[key] = temp_surface.copy()

def draw_transparent_circle(screen, center, radius, color, alpha, thickness=0, cache={}):
    # check if the circle has already been rendered with the same parameters
    key = (center, radius, color, alpha, thickness)
    if key in cache:
        screen.blit(cache[key], (0, 0))
        return

    # create a temporary surface to handle transparency
    temp_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    rgba_color = color + (alpha,)  # Create RGBA color tuple

    # draw the circle on the temporary surface
    pygame.draw.circle(temp_surface, rgba_color, center, radius, thickness)

    # blit the temporary surface onto the main screen surface
    screen.blit(temp_surface, (0, 0))

    # cache the rendered circle
    cache[key] = temp_surface.copy()

def write_centered_text(screen, text, rect, colour, cache={}):
    # convert rect to a tuple to use it as a key in the cache
    rect_tuple = (rect.x, rect.y, rect.width, rect.height)

    # check if the text has already been rendered with the same parameters
    key = (text, rect_tuple, colour)
    if key in cache:
        for text_surface, x, y in cache[key]:
            screen.blit(text_surface, (x, y))
        return

    # split the text into lines and calculate the size of the text
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
        # calculate the mid font size
        mid = (low + high + 1) // 2
        
        # check if the text fits in the rect with the current font size
        font_obj = pygame_font.Font(None, mid)
        line_sizes = [(line, font_obj.size(line)) for line in lines]
        text_height = sum(size[1] for _, size in line_sizes)
        text_width = max(size[0] for _, size in line_sizes)

        # update the bounds of the binary search
        if text_height <= rect.height and text_width <= rect.width:
            low = mid
        else:
            high = mid - 1

    # render the text with the maximum font size
    font_size = low
    font_obj = pygame_font.Font(None, font_size)
    line_sizes = [(line, font_obj.size(line)) for line in lines]
    text_height = sum(size[1] for _, size in line_sizes)
    text_width = max(size[0] for _, size in line_sizes)

    # cache the rendered text
    cache[key] = []
    y = rect.y + (rect.height - text_height) // 2
    for i, (line, size) in enumerate(line_sizes):

        # render the text
        text_surface = font_obj.render(line, True, colour)
        x = rect.x + (rect.width - size[0]) // 2
        screen.blit(text_surface, (x, y + i * size[1]))

        # cache the rendered text
        cache[key].append((text_surface, x, y + i * size[1]))

def draw_transparent_rect(screen, rect, color, alpha, thickness=0, cache={}):
    # check if the rectangle has already been rendered with the same parameters
    key = (rect, color, alpha, thickness)
    if key in cache:
        screen.blit(cache[key], (0, 0))
        return

    # create a temporary surface to handle transparency
    temp_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    rgba_color = color + (alpha,)  # create RGBA color tuple

    # draw the rectangle on the temporary surface
    pygame.draw.rect(temp_surface, rgba_color, rect, thickness)

    # blit the temporary surface onto the main screen surface
    screen.blit(temp_surface, (0, 0))

    # cache the rendered rectangle
    cache[key] = temp_surface.copy()

class Button:
    def __init__(self, screen, text, rect, action, base_color, hover_color, clicked_color, text_color, descriptive_text=None):
        self.screen = screen
        self.text = text
        self.rect = rect
        self.action = action
        self.base_color = base_color
        self.hover_color = hover_color
        self.clicked_color = clicked_color
        self.text_color = text_color
        self.descriptive_text = descriptive_text

    def draw(self, mx, my, mb):
        if self.rect.collidepoint(mx, my):
            # hover color
            pygame.draw.rect(self.screen, self.hover_color, self.rect)

            if mb[0]:
                # clicked color
                pygame.draw.rect(self.screen, self.clicked_color, self.rect)
            
            # draw the descriptive text above the button
            if self.descriptive_text:
                offset = 50
                descriptive_text_rect = pygame.Rect(self.rect.x, self.rect.y - offset, self.rect.width, offset)
                
                # draw a rectangle for the descriptive text
                pygame.draw.rect(self.screen, self.clicked_color, descriptive_text_rect)

                # write the descriptive text
                write_centered_text(self.screen, self.descriptive_text, descriptive_text_rect, self.hover_color)
        else:
            # base color
            pygame.draw.rect(self.screen, self.base_color, self.rect)

        # write the text on the button
        write_centered_text(self.screen, self.text, self.rect, self.text_color)

        # draw an outline around the button (bigger rectangle)
        outline_rect = pygame.Rect(self.rect.x - 5, self.rect.y - 5, self.rect.width + 10, self.rect.height + 10)
        pygame.draw.rect(self.screen, (0, 0, 0), outline_rect, 5)


    def check_click(self, mx, my, L_mouse_up):
        # check if the button was clicked
        if self.rect.collidepoint(mx, my) and L_mouse_up:
            return self.action
        return None