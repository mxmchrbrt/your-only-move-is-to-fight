import pygame
import bot
import character
import client
import config
import launcher
import menu
import player
import server
import terrains
import ui_logic as uil
import ui

pygame.init()


# Fullscreen at native resolution

round_clock = uil.ClockTimer()
keyguide = ui.KeyGuide()
ui_arrow = ui.PlayerPointer()

def ResetPlayers(playerlist):
    for player_id, player in enumerate(playerlist, 1):
        player.knockout = False
        player.stock = 3
        player.percentage = 0
        if player_id == 1:
            player.position = [400, 710]
        else :
            player.position = [1200, 200]

def UpdatePlayers(playerlist):
    if game_mode != "train":
        for player_id, player in enumerate(playerlist, 1):
            ui_arrow.track(config.screen,player)
            if not player.knockout:
                player.key(client)
                if player_id == 1:
                    enemy = playerlist[1]
                else:
                    enemy = playerlist[0]
                player.movementupdate(client, enemy = enemy)
                ui_logic.UpdateUI(player_id,player)
                if player.stock <= 0:
                    player.knockout = True
            else:
                ui_logic.Death(round_clock)
    else:
        for player_id, player in enumerate(playerlist, 1):
            ui_arrow.track(config.screen,player)
            player.key(client)
            if player_id == 1:
                enemy = playerlist[1]
            else:
                enemy = playerlist[0]
            player.movementupdate(client, enemy = enemy)

# Fullscreen at native resolution
def game(game_mode, server_ip):
    screen = config.screen    
    print(f"Game mode: {game_mode}, Server IP: {server_ip}")
    if game_mode == "online":
        launcher.launch_online_game()
    elif game_mode == "lan_host":
        launcher.launch_lan_host_game()
    elif game_mode == "lan_client":
        launcher.launch_lan_client_game(server_ip)
    elif game_mode == "solo":
        pass
    count = 0
    print("Waiting for server connection...")
    if not(game_mode == "solo" or game_mode == "train") :
        while not client.is_connected():
            if count == 10:
                return
            pygame.time.wait(100)
            count +=1
        print("Connected! Starting game...")

    clock = pygame.time.Clock()
    running = True
    grounds = []
    grounds.append(terrains.Ground(config.screen, 175, 1664, 710))
    grounds.append(terrains.Ground(config.screen, 1139, 1599, 411))
    grounds.append(terrains.Ground(config.screen, 271, 785, 255))
    bg = pygame.image.load(config.resource_path("assets/bg.png")).convert()
    bg = pygame.transform.smoothscale(bg, menu_instance.screen_size)
    debug = True if game_mode == "train" else False 
    local = player.Player("You", grounds, debug = debug )
    if game_mode == "solo":
        remote = bot.Bot(grounds)#difficulty=server_ip
    else :
        remote = player.DistantPlayer("Opponent", grounds)

    players = [local, remote]
    screen_w, screen_h = config.screen_size[0], config.screen_size[1]

    # Initialize damage display UI
    if game_mode != "train":
        damage_display = ui.DamageDisplay()
        damage_display.add_player(1, players[0].name, 1, 3)
        damage_display.add_player(2, players[1].name, 4, 3)
        global ui_logic
        ui_logic = uil.UILogic(players,damage_display)
    pygame.mixer.init()
    ingamemusic = config.resource_path("assets/sounds/ingame_ambiance.mp3")
    pygame.mixer.music.load(ingamemusic)
    pygame.mixer.music.play(-1)
    
    while running:
        config.screen.blit(bg, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LSHIFT:
                    local.shield()
                if event.key == pygame.K_ESCAPE:
                    return
                if event.key == pygame.K_SPACE: # space = jump 
                    if pygame.key.get_pressed()[pygame.K_e]: # space + f = uppunch
                        local.uppunch()
                        local.dojump()
                    else:
                        local.dojump()
                      # ESPACE seul = saut normal
                if event.key == pygame.K_e:
                    local.punching()
                if event.key == pygame.K_f:
                    if pygame.key.get_pressed()[pygame.K_s]:
                        local.lowkick()    # ← remplace local.is_jumping
                    else:
                        local.midkick()
            if event.type == pygame.JOYBUTTONDOWN:
                if event.button == 0:
                        local.dojump()
                if event.button == 2:
                    if config.controller.get_axis(1) < -0.3:
                        local.uppunch()  # E + ESPACE = uppunch
                        local.dojump()
                    else:
                        local.punching()
                if event.button == 1:
                    if config.controller.get_axis(1) > 0.1:
                        local.lowkick()
                    else:
                        local.midkick()
                if event.button == 3:
                    local.shield()
            if event.type == pygame.JOYDEVICEADDED:
                config.controller = pygame.joystick.Joystick(0)
            if event.type == pygame.MOUSEBUTTONDOWN:
                if ui_logic.back_button.checkForInput(pygame.mouse.get_pos()):
                    server.serverrun = False
                    del players[0]
                    return
                    #pygame.mixer.init()
                    music = config.resource_path("assets/sounds/menu_sound.mp3")
                    pygame.mixer.music.load(music)
                    pygame.mixer.music.play(-1,30.00,1000)
                    ResetPlayers(players)
                    round_clock.ResetTimer()
        # RENDER YOUR GAME HERE

        UpdatePlayers(players)
        round_clock.UpdateTimer()
        pygame.display.flip()
        clock.tick(60)
        
round_clock = uil.ClockTimer() 
menu_instance = menu.GameMenu()
ui_arrow = ui.PlayerPointer()
running = True
while(running):
    server.serverrun = False
    client.clientrun = False
    game_mode, server_ip = menu_instance.run()
    game(game_mode, server_ip)
pygame.quit()
