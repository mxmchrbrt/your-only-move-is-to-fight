import math
from os import isatty
import attacks
import pygame
import config
import sfx

class Character(pygame.sprite.Sprite):
    def __init__(self, grounds, debug = False, color = (0,0,0)):
        self.stock = 3
        self.speed = 7
        self.yvelocity = 10
        self.xvelocity = 0
        self.position = [400, -400]
        self.percentage = 0
        self.jump = 2
        self.gravity = 3
        self.friction = 2
        self.stun = [0, 0, 0] #0 stun 1 freeze 2 invulnerability
        self.grounds = grounds
        self.jumppower = 40
        self.maxjump = 2
        self.knockout = False
        self.direction = 0 #0 gauche 1 droite
        self.ismoving = 0
        self.isattacking = False
        self.hitbox = attacks.Hitbox(0,0,0,0)
        self.attaque_punch = attacks.attack(sfx.punch,4, 2, 90,55,25,-170,frame_start=2,frame_end=4)
        self.attaque_unpunch = attacks.attack(sfx.uppunch,7, 4, 70, 100, -10,-320,frame_start=5, frame_end=9)
        self.attaque_midkick = attacks.attack(sfx.midkick,5, 3, 100,50, 20,-145,frame_start=3, frame_end=6)
        self.attaque_lowkick = attacks.attack(sfx.lowkick,3,1 ,85 ,45 ,15,-80,frame_start=2,frame_end=5)
        self.listeattaque = [self.attaque_midkick, self.attaque_punch, self.attaque_unpunch, self.attaque_lowkick]
        self.debug = debug
        self.animation = {}
        init_animation(self.animation, color)
        self.facing_right = True  # pour savoir le sens lors du saut
        self.shield_duration = 0
        
    def resetanim(self):
        for i in self.animation:
            self.animation[i]["is"] = False
            self.animation[i]['sprite'] = 0

    def knockback(self, attacker, power):
        dy = self.position[1] - attacker.position[1]
        dx = self.position[0] - attacker.position[0]
        if dx == 0 and dy == 0:
            dist = 1
        else:
            dist = math.sqrt(dy**2 + dx**2)
        vecty = power * (1 + 2**(self.percentage // 10)) * dy / dist + power*4
        vectx = power * (4 + (self.percentage/ 7)) * dx / dist
        self.yvelocity += int(vecty)
        self.xvelocity += int(vectx)

    def touchingground(self):
        for i in self.grounds:
            if self.position[1] < i.height and self.position[1] - self.yvelocity + self.gravity > i.height:
                if self.position[0] >= i.start and self.position[0] <= i.stop:
                    self.position[1] = i.height
                    self.yvelocity = 0
                    return True
            if self.position[1] == i.height:
                if self.position[0] >= i.start and self.position[0] <= i.stop:
                    return True

    def isfalling(self):
        if self.touchingground():
            self.jump = self.maxjump
            if self.yvelocity < 0:
                self.yvelocity = 0
            return False
        else:
            self.yvelocity -= self.gravity
            return True

    def dojump(self):
        if (self.jump > 0 or self.touchingground()) and not self.animation["shield"]['is']:
            self.jump -= 1
            self.yvelocity = self.jumppower
            if not self.animation["uppunch"]["is"] or not self.isattacking:
                self.animation["jump"]["is"] = True
                self.animation["jump"]["sprite"] = 0

    def update_jump_animation(self):
        if self.animation["jump"]["is"]:
            offset_x = -40
            offset_y = -250
            frame = self.animation["jump"]["keyframe"][int(self.animation["jump"]["sprite"])]
            if not self.facing_right:
                frame = pygame.transform.flip(frame, True, False)
            config.screen.blit(frame, ((self.position[0] + offset_x) * config.scaleX, (self.position[1] + offset_y) * config.scaleY))
            self.animation["jump"]["sprite"] += 0.8
            if self.animation["jump"]["sprite"] >= 21:
                self.animation["jump"]["is"] = False

    def uppunch(self):
        if self.animation["uppunch"]["sprite"] == 0 and self.animation["uppunch"]['is'] == False and self.isattacking == False:
            self.resetanim()
            self.animation["uppunch"]["is"] = True
            self.animation["punch"]["is"] = False
            self.animation["uppunch"]["sprite"] = 0
            self.attaque_unpunch.sound.play()
            self.attaque_unpunch.reset()
            self.isattacking = True

    def update_uppunch(self, enemy=None):
        offset_x = -40
        offset_y = -250
        frame = self.animation["uppunch"]["keyframe"][int(self.animation["uppunch"]["sprite"])]
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)
        config.screen.blit(frame, ((self.position[0] + offset_x) * config.scaleX, (self.position[1] + offset_y) * config.scaleY))
        real_offsetX = self.attaque_unpunch.offsetX if self.facing_right else -self.attaque_unpunch.offsetX - self.attaque_unpunch.width
        if self.attaque_unpunch.is_active(self.animation["uppunch"]["sprite"]):
            self.attaque_unpunch.attackperso(self, enemy)
            if self.attaque_unpunch.hitbox and self.debug:
                self.attaque_unpunch.hitbox.drawhitbox()
        self.animation["uppunch"]["sprite"] += 0.8
        self.stopx()
        if self.animation["uppunch"]["sprite"] >= 17:
            self.animation["uppunch"]["is"] = False
            self.animation["uppunch"]["sprite"] = 0
            self.attaque_unpunch.reset()
            self.isattacking = False

    def midkick(self):
        if self.animation["midkick"]["sprite"] == 0 and self.animation["midkick"]['is'] == False and self.isattacking == False:
            self.resetanim()
            self.animation["midkick"]["is"] = True
            self.animation["midkick"]["sprite"] = 0
            self.attaque_midkick.sound.play()
            self.attaque_midkick.reset()
            self.isattacking = True
            

    def update_midkick(self, enemy=None):
        offset_x = -40
        offset_y = -250
        frame = self.animation["midkick"]["keyframe"][int(self.animation["midkick"]["sprite"])]
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)
            offset_x = -90
        config.screen.blit(frame, ((self.position[0] + offset_x) * config.scaleX, (self.position[1] + offset_y) * config.scaleY))
        self.animation["midkick"]["sprite"] += 0.6
        real_offsetX = self.attaque_midkick.offsetX if self.facing_right else -self.attaque_midkick.offsetX - self.attaque_midkick.width
        if self.attaque_midkick.is_active(self.animation["midkick"]["sprite"]):
            self.attaque_midkick.attackperso(self, enemy)
            if self.attaque_midkick.hitbox and self.debug:
               self.attaque_midkick.hitbox.drawhitbox  
        self.stopx()
        if self.animation["midkick"]["sprite"] >= 7:
            self.animation["midkick"]["sprite"] = 0
            self.animation["midkick"]["is"] = False
            self.attaque_midkick.reset()
            self.isattacking = False

    def lowkick(self):
        if self.animation["lowkick"]["sprite"] == 0 and self.animation["lowkick"]['is'] == False and self.isattacking == False:
            self.resetanim()
            self.animation["lowkick"]["is"] = True
            self.animation["lowkick"]["sprite"] = 0
            self.isattacking = True
            self.attaque_lowkick.sound.play()
            self.attaque_lowkick.reset()
    def update_lowkick(self, enemy=None):
        offset_x = -40
        offset_y = -250
        frame = self.animation["lowkick"]["keyframe"][int(self.animation["lowkick"]["sprite"])]
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)
            offset_x = -70
        config.screen.blit(frame, ((self.position[0] + offset_x) * config.scaleX, (self.position[1] + offset_y) * config.scaleY))
        real_offsetX = self.attaque_lowkick.offsetX if self.facing_right else -self.attaque_lowkick.offsetX - self.attaque_lowkick.width
        if self.attaque_lowkick.is_active(self.animation["lowkick"]["sprite"]):
            self.attaque_lowkick.attackperso(self, enemy)
            if self.attaque_lowkick.hitbox and self.debug:
                self.attaque_lowkick.hitbox.drawhitbox()
        self.stopx()
        self.animation["lowkick"]["sprite"] += 0.6
        if self.animation["lowkick"]["sprite"] >= 7:
            self.animation["lowkick"]["sprite"] = 0
            self.animation["lowkick"]["is"] = False
            self.isattacking = False
            self.attaque_lowkick.reset()
    def punching(self):
        if self.animation["punch"]["sprite"] == 0 and self.animation["punch"]['is'] == False and self.isattacking == False: 
            self.resetanim()
            self.animation["punch"]["is"] = True
            self.animation["punch"]["sprite"] = 0
            self.attaque_punch.sound.play()
            self.attaque_punch.reset()
            self.isattacking = True
    def update_punch(self, enemy=None):
        offset_x = -30
        offset_y = -250
        frame = self.animation["punch"]["keyframe"][int(self.animation["punch"]["sprite"])]
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)
            offset_x = -80
        config.screen.blit(frame, ((self.position[0] + offset_x) * config.scaleX, (self.position[1] + offset_y) * config.scaleY))
        real_offsetX = self.attaque_punch.offsetX if self.facing_right else -self.attaque_punch.offsetX - self.attaque_punch.width
        if self.attaque_punch.is_active(self.animation["punch"]["sprite"]):
            self.attaque_punch.attackperso(self, enemy)
            if self.attaque_punch.hitbox and self.debug:
                self.attaque_punch.hitbox.drawhitbox()
        self.stopx()
        self.animation["punch"]["sprite"] += 0.6
        if self.animation["punch"]["sprite"] >= 7:
            self.animation["punch"]["sprite"] = 0
            self.animation["punch"]["is"] = False
            self.isattacking = False
            self.attaque_punch.reset()

    def gotoright(self, modifier = 1):
        if self.stun[0] == 0 and self.isattacking == False:
            self.facing_right = True
            self.animation["run"]["is"] = True
            offset_x = -40
            offset_y = -250
            frame = self.animation["run"]["keyframe"][int(self.animation["run"]["sprite"])]
            if (not self.shield and not self.animation["jump"]["is"] and not self.animation["punch"]["is"]
                    and not self.animation["midkick"]["is"] and not self.animation["uppunch"]["is"]
                    and not self.animation["lowkick"]["is"]):
                config.screen.blit(frame, ((self.position[0] + offset_x) * config.scaleX, (self.position[1] + offset_y) * config.scaleY))
            self.animation["run"]["sprite"] += 0.6*modifier
            if self.animation["run"]["sprite"] >= 12:
                self.animation["run"]["sprite"] = 0
            if self.xvelocity < math.ceil(self.speed*modifier):
                self.xvelocity += math.ceil(self.speed*modifier)
            elif self.xvelocity == math.ceil(self.speed*modifier):
                self.xvelocity = math.ceil(self.speed*modifier)
            else:
                self.xvelocity -= 1
                    
    def gotoleft(self, modifier = 1):
        if self.stun[0] == 0 and self.isattacking == False:
            self.facing_right = False
            self.animation["run"]["is"] = True
            self.animation["run"]["sprite"] += 0.6*modifier
            if self.animation["run"]["sprite"] >= 12:
                self.animation["run"]["sprite"] = 0
            offset_x = -40
            offset_y = -250
            frame = self.animation["run"]["keyframe"][int(self.animation["run"]["sprite"])]
            if (not self.shield and not self.animation["jump"]["is"] and not self.animation["punch"]["is"]
                    and not self.animation["midkick"]["is"] and not self.animation["uppunch"]["is"]
                    and not self.animation["lowkick"]["is"]): 
                flipped = pygame.transform.flip(frame, True, False)
                config.screen.blit(flipped, ((self.position[0] + offset_x) * config.scaleX, (self.position[1] + offset_y) * config.scaleY))
            if self.xvelocity > -math.ceil(self.speed*modifier):
                self.xvelocity -= math.ceil(self.speed*modifier)
            elif self.xvelocity == -math.ceil(self.speed*modifier):
                self.xvelocity = -math.ceil(self.speed*modifier)
            else:
                self.xvelocity += 1

    def death(self, net=None):
        if (
            self.position[1] > 2000
            or self.position[0] > 2000
            or self.position[0] < -2000
        ):
            self.stock -= 1
            self.percentage = 0
            self.position = [1200, -200]
            self.xvelocity = 0
            self.yvelocity = 0

    def stopx(self):
        self.animation['run']['is'] = False
        if self.xvelocity != 0:
            if self.xvelocity < 0:
                self.xvelocity += 2
            if self.xvelocity > 0:
                self.xvelocity -= 2
            if self.xvelocity == -1 or self.xvelocity == 1:
                self.xvelocity = 0

    def static(self):
        offset_x = -30
        offset_y = -250
        if self.animation["static"]["sprite"] >= 7:
            self.animation["static"]["sprite"] = 0
        frame = self.animation["static"]["keyframe"][int(self.animation["static"]["sprite"])]
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)
        config.screen.blit(frame, ((self.position[0] + offset_x) * config.scaleX, (self.position[1] + offset_y) * config.scaleY))
        self.animation["static"]["sprite"] += 0.5
        
    def shield(self):
        if self.animation["shield"]["sprite"] == 0 and self.animation["shield"]['is'] == False and self.isattacking == False:
            if self.xvelocity >= -self.speed-1 and self.xvelocity <= self.speed + 1:
                self.xvelocity = 0
            self.resetanim()
            self.animation["shield"]['is'] = True
            self.isattacking = True

    def update_shield(self):
        if self.animation["shield"]['is']:
            offset_x = -60
            offset_y = -300
            # Show frame_3 (the main shield image) while shield is active
            frame = self.animation["shield"]["keyframe"][int(self.animation["shield"]["sprite"])]
            if not self.facing_right:
                frame = pygame.transform.flip(frame, True, False)
            config.screen.blit(frame, ((self.position[0] + offset_x + 20) * config.scaleX, (self.position[1] + offset_y + 40) * config.scaleY))
            if int(self.animation["shield"]["sprite"]) == 3:
                self.animation["shield"]["sprite"] += 0.05
            else :
                self.animation["shield"]["sprite"] += 0.6
            if self.animation["shield"]["sprite"] >= 7:
                self.animation["shield"]["sprite"] = 0
                self.animation["shield"]["is"] = False
                self.isattacking = False 

    def movementupdate(self, net=None, enemy=None):
        self.isfalling()
        self.death(net)
        self.hitbox.update(((self.position[0] -28) *config.scaleX, (self.position[0] + 28)*config.scaleX,  (self.position[1] -235)*config.scaleY,  (self.position[1])*config.scaleY))  
        if self.debug:
            self.hitbox.drawhitbox()
        if self.stun[0] != 0:
            self.stun[0] -=1
        else:
            self.priority_animation(enemy)
        if enemy:
            if self.stun[2] == 0:
                self.getcollided(enemy)
            else:
                self.stun[2] -= 1
        if self.stun[1] == 0:
            self.position[0] += self.xvelocity
            self.position[1] -= self.yvelocity
        else:
            self.stun[1] -= 1
    def getcollided(self, enemy = None):
        if enemy:
            for attaque in enemy.listeattaque:
                if attaque.hitbox:
                    if self.hitbox.collide(attaque.hitbox) and not attaque.has_hit and not self.animation["shield"]["is"]:
                        attaque.has_hit = True
                        attaque.hitbox = None
                        self.stun = [abs(attaque.frame_end - attaque.frame_start), abs(attaque.frame_start), abs(attaque.frame_end - attaque.frame_start)]
                        self.knockback(enemy, attaque.power)
                        self.percentage += attaque.damage
                        
    def priority_animation(self, enemy=None):
        if self.animation["shield"]['is']:
            self.update_shield()
        elif self.animation["uppunch"]["is"]:
            self.update_uppunch(enemy)
        elif self.animation["lowkick"]["is"]:
            self.update_lowkick(enemy)
        elif self.animation["punch"]["is"]:
            self.update_punch(enemy)
        elif (not self.animation["punch"]["is"] and self.animation["midkick"]["is"]):
            self.update_midkick(enemy)
        elif self.animation["jump"]["is"]:
            self.update_jump_animation()
        elif self.animation["run"]["is"]:
            frame = self.animation["run"]["keyframe"][int(self.animation["run"]["sprite"])]
            if not self.facing_right:
                frame = pygame.transform.flip(frame, True, False)
            config.screen.blit(frame, ((self.position[0] - 40) * config.scaleX,(self.position[1] - 250) * config.scaleY))
        elif not self.animation["run"]["is"]:
            self.static()


def scale_frames(anim_dict):
    for anim_name in anim_dict:
        for i, frame in enumerate(anim_dict[anim_name]["keyframe"]):
            w, h = frame.get_size()
            anim_dict[anim_name]["keyframe"][i] = pygame.transform.scale(
                frame, (int(w * config.scaleX), int(h * config.scaleY))
            )
def convert(img, color):
    px = pygame.PixelArray(img)
    px.replace((0, 0, 0), color)
    del px
    return img
def init_animation(dict, color = (0,0,0)):
    
    dict["run"] = {}
    dict["run"]['keyframe'] = []
    dict["run"]['is'] = False
    dict["run"]['sprite'] = 0
    # def of sprite for run
    for i in range(13):
        dict["run"]["keyframe"].append(convert(pygame.image.load(config.resource_path("assets/run/frame_"+str(i)+".png")).convert_alpha(), color))
     
    dict["jump"] = {}
    dict["jump"]["keyframe"] = []
    dict["jump"]["is"] = False
    dict["jump"]["sprite"] = 0

    for i in range(22):
        dict["jump"]["keyframe"].append(convert(pygame.image.load(config.resource_path("assets/jump/frame_"+str(i)+".png")).convert_alpha(), color))
    dict["punch"] = {}
    dict["punch"]["keyframe"] = []
    dict["punch"]["is"] = False
    dict["punch"]["sprite"] = 0
    for i in range(8):
        dict["punch"]["keyframe"].append(convert(pygame.image.load(config.resource_path("assets/punch/frame_"+str(i)+".png")).convert_alpha(), color))
    dict["uppunch"] = {}
    dict["uppunch"]["keyframe"] = []
    dict["uppunch"]["is"] = False
    dict["uppunch"]["sprite"] = 0
    for i in range(18):
        dict["uppunch"]["keyframe"].append(convert(pygame.image.load(config.resource_path("assets/uppunch/frame_"+str(i)+".png")).convert_alpha(), color))
    dict["midkick"] = {}
    dict["midkick"]["keyframe"] = []
    dict["midkick"]["is"] = False
    dict["midkick"]["sprite"] = 0
    for i in range(12):
        dict["midkick"]["keyframe"].append(convert(pygame.image.load(config.resource_path("assets/midkick/frame_"+str(i)+".png")).convert_alpha(), color))
    dict["lowkick"] = {}
    dict["lowkick"]["keyframe"] = []
    dict["lowkick"]["is"] = False
    dict["lowkick"]["sprite"] = 0
    for i in range(8):
        dict["lowkick"]["keyframe"].append(convert(pygame.image.load(config.resource_path("assets/lowkick/frame_"+str(i)+".png")).convert_alpha(), color))
    dict["static"] = {}
    dict["static"]["keyframe"] = []
    dict["static"]["is"] = False
    dict["static"]["sprite"] = 0
    for i in range(8):
        dict["static"]["keyframe"].append(convert(pygame.image.load(config.resource_path("assets/static/frame_"+str(i)+".png")).convert_alpha(), color))
    dict["shield"] = {}
    dict["shield"]["keyframe"] = []
    dict["shield"]["is"] = False
    dict["shield"]["sprite"] = 0
    for i in range(7):
        dict["shield"]["keyframe"].append(convert(pygame.image.load(config.resource_path("assets/shield/frame_"+str(i)+".png")).convert_alpha(), color))
    
