import character 
import pygame
import config
import sfx

class Hitbox :
    def __init__(self, left, right,top, bottom):
        self.left = left
        self.right = right
        self.top = top
        self.bottom = bottom
    def update(self, tuple):
        self.left = tuple[0]
        self.right = tuple[1]
        self.top = tuple[2]
        self.bottom = tuple[3]
    def drawhitbox(self):
        pygame.draw.rect(config.screen, [0,255,0], [self.left, self.top, self.right-self.left, self.bottom-self.top], 2)
    def collide(self, other):
        if self.left < other.right and self.right > other.left and self.top < other.bottom and self.bottom > other.top:
            return True
        else :
            return False
class attack :
    def __init__(self, sound, damage, power, width, height, offsetX,offsetY,frame_start=2, frame_end=5):
        self.sound = sound
        self.damage = damage
        self.power = power
        self.width = width
        self.height = height
        self.offsetX =offsetX
        self.offsetY = offsetY
        self.frame_start = frame_start
        self.frame_end = frame_end
        self.hitbox = None
        self.has_hit = False


    def reset(self):
        self.has_hit =False
        self.hitbox = None
        
    def is_active(self, sprite_index):
        return self.frame_start <= int(sprite_index) <= self.frame_end

    def attackperso(self, attacker, enemy):
        if self.has_hit:
            return
        real_offsetX = self.offsetX if attacker.facing_right else -self.offsetX - self.width
        attackhitbox = Hitbox(attacker.position[0] + real_offsetX ,attacker.position[0] + real_offsetX+self.width, attacker.position[1] + self.offsetY, attacker.position[1]+self.offsetY+self.height)
        self.hitbox = attackhitbox
