import pygame

import character
import client
import config
import launcher
import menu
import player
import server
import terrains
import ui

class UILogic:

    def __init__(self, playerlist, damage_display):
        self.death_display = ui.DeathUI()
        self.playerlist = playerlist
        self.damage_display = damage_display

        ##Respawn button
        self.back_button = menu.Button(
        image=pygame.image.load(config.resource_path("assets/MenuBox.png")),
        pos=(config.SCREEN_W // 2,(config.SCREEN_H // 2) + (config.SCREEN_H // 3)),
        text_input="BACK         ",
        font=pygame.font.Font(config.resource_path("assets/GochiHand-Regular.ttf"), 70),
        base_color="#ffffff",
        hovering_color="Orange",
        )

    def UpdateUI(self,player_id,player):
        self.damage_display.update(player_id, player.percentage)
        self.damage_display.set_stocks(player_id, player.stock)
        self.damage_display.draw(config.screen)

    def Death(self,clock):
        for i in self.playerlist:
            if i.knockout == False: winner = i.name
        self.death_display.draw(config.screen, winner,clock.round_clock)
        ## Restart button
        clock.timer_stop = True
        self.back_button.changeColor(pygame.mouse.get_pos())
        self.back_button.update(config.screen)

class ClockTimer:

    def __init__(self):
        self.round_timer = ui.RoundTimer()
        self.round_clock = 0
        self.timer_stop = False

    def UpdateTimer(self):
        if not self.timer_stop:
            self.round_clock += 1 / 60
            self.round_timer.draw(config.screen, round(self.round_clock))

    def ResetTimer(self):
        self.round_clock = 0
        self.timer_stop = False