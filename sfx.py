import pygame
import config

pygame.init()
pygame.mixer.init()
#volume = float(input("Volume : Between 0.0 and 1.0: "))
pygame.mixer.music.set_volume(1)

#midkick = pygame.mixer.Sound("asset/midkick/midkick.mp3")
#jump =  pygame.mixer.Sound("asset/jump/jump.mp3")
lowkick = pygame.mixer.Sound(config.resource_path("assets/punch/lowkick.mp3"))
midkick = pygame.mixer.Sound(config.resource_path("assets/punch/midkick.mp3"))
punch = pygame.mixer.Sound(config.resource_path("assets/punch/punch.mp3"))
#run = pygame.mixer.Sound("asset/run/run.mp3")
uppunch = pygame.mixer.Sound(config.resource_path("assets/uppunch/uppunch.mp3")) 
running = pygame.mixer.Sound(config.resource_path("assets/run/running.mp3")) 
#running = pygame.mixer.Sound("assets/running/running.mp3") 
