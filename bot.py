import character
import random

class Bot(character.Character):
    def __init__(self, grounds, difficulty = "medium"):
        character.Character.__init__(self, grounds, color=(255, 0, 0) )
        self.name = "Kevin"
        self.jump_cooldown = 0
        self.attack_cooldown = 0
        self.jumppower=52
        self.position = [1200, 200]

        if difficulty == "easy":
            self.reaction = 20
            self.shield_chance = 0.1
        elif difficulty == "medium" :
            self.reaction = 10
            self.shield_chance = 0.2
        elif difficulty == "hard":
            self.reaction = 0
            self.shield_chance = 1.00


    def key(self, net):
        pass


    def update(self, enemy):
        distance = abs(self.position[0] -enemy.position[0])
        hauteur = abs(self.position[1] - enemy.position[1])
        is_attacking = (self.animation["uppunch"]["is"] or self.animation["punch"]["is"] or self.animation["lowkick"]["is"] or self.animation["midkick"]["is"])
        enemy_attacking = (enemy.animation["punch"]["is"] or enemy.animation["uppunch"]["is"] or enemy.animation["lowkick"]["is"] or enemy.animation["midkick"]["is"])


        if enemy.position[0] > self.position[0]:
            self.facing_right = True
        else :
            self.facing_right = False

        if enemy_attacking and distance < 100 and not self.isattacking and random.random() < self.shield_chance:
            self.shield()


        if not is_attacking :
            if distance > 100:
                if self.position[0] - enemy.position[0] >0:
                    self.gotoleft()
                else :
                    self.gotoright()
            else :
                self.stopx()

            if not self.animation["punch"]["is"] and not self.animation["uppunch"]["is"] and not self.animation["midkick"]["is"] and not self.animation["lowkick"]["is"] :
                if self.attack_cooldown == 0:
                    if hauteur < 100 and distance < 100 and enemy.position[1] < self.position[1]:
                        self.uppunch()
                    elif hauteur < 100 and distance < 100:
                        random.choice([self.punching, self.midkick, self.lowkick])()
                    self.attack_cooldown= self.reaction
    
        if self.position[1] - enemy.position[1] >200 and self.touchingground() and self.jump_cooldown == 0 and self.percentage<80 and distance<100:
            self.dojump()
            self.jump_cooldown = 20

        if self.position[1] - enemy.position[1] >200 and not self.touchingground() and self.jump==1 and self.percentage<=80 and distance < 100:
            self.dojump()
            self.jump_cooldown =20

        if self.jump_cooldown >0:
            self.jump_cooldown -= 1
        if self.attack_cooldown >0:
            self.attack_cooldown -=1            


    def movementupdate(self, net, enemy=None):
        self.update(enemy)
        character.Character.movementupdate(self, net=None, enemy=enemy)
