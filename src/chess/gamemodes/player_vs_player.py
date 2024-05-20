import pygame




class PlayerVsPlayer:
    def __init__(self, screen):
        self.screen = screen
    







    def main_loop(self):
        running = True

        self.lmx, self.lmy = pygame.mouse.get_pos()
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return 'exit'
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.lmx, self.lmy = pygame.mouse.get_pos()
                    
            self.mx, self.my = pygame.mouse.get_pos()

            self.screen.fill((255, 255, 255)) # replace this with a background image

            




            pygame.display.flip()