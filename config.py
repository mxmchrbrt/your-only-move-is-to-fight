import os
import sys

import pygame
import terrains


def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


pygame.init()

## Init screen
info = pygame.display.Info()
SCREEN_W = info.current_w
SCREEN_H = info.current_h
## Fullscreen at native resolution
screen = pygame.display.set_mode((SCREEN_W, SCREEN_H), pygame.FULLSCREEN)
pygame.joystick.init()
if pygame.joystick.get_count() != 0:
    controller = pygame.joystick.Joystick(0)
else:
    controller = None
## Define scalars
refX, refY = 1920, 1080
refX, refY = 1920, 1080
scaleX, scaleY = (SCREEN_W / refX),(SCREEN_H / refY)
screen_size = (SCREEN_W, SCREEN_H)

screen.fill("black")
