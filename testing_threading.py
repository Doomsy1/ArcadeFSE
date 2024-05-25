import pygame
import random
import time
import threading

pygame.init()

window_width = 800
window_height = 600
window = pygame.display.set_mode((window_width, window_height))


def random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def caount(result_container):
    start_time = time.time()
    
    counter = 0
    while counter < 20000000:
        counter += 1

    end_time = time.time()
    elapsed_time = end_time - start_time 
    print(f"Time taken: {elapsed_time:.2f} seconds")
    result_container.append(elapsed_time)

fps = 60
clock = pygame.time.Clock()

counting_result = []

running = True
saved_time = 0
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not counting_result:
                threading.Thread(target=caount, args=(counting_result,)).start()

    window.fill(random_color())

    if counting_result:
        saved_time = counting_result[0]
        counting_result.clear()
    if saved_time:
        font = pygame.font.Font(None, 36)
        text = font.render(f"Time taken: {saved_time:.2f} seconds", True, (255, 255, 255))
        window.blit(text, (20, 20))

    pygame.display.flip()

    clock.tick(fps)

pygame.quit()
