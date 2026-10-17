import pygame
class Ground:
    def __init__(self, screen, start, stop, height):
        self.start = start
        self.stop = stop
        self.height = height
        pygame.draw.rect(screen, [255, 255, 255], [self.start, self.height, 1200, 100], 0)
