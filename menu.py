import socket
import sys
import threading
import config
import pygame

pygame.mixer.init()
mixer_initialized = True
music = config.resource_path("assets/sounds/menu_sound.mp3")
pygame.mixer.music.load(music)
pygame.mixer.music.play()
button_select_sound = pygame.mixer.Sound(config.resource_path("assets/sounds/button_select.mp3"))
button_select_sound.set_volume(0.5)

class Button:
    def __init__(
        self,
        image,
        pos,
        text_input,
        font,
        base_color,
        hovering_color,
        text_align="center",
        padding=30,
    ):
        self.image = image
        self.x_pos, self.y_pos = pos
        self.font = font
        self.base_color = base_color
        self.hovering_color = hovering_color
        self.text_input = text_input

        self.text_align = text_align
        self.padding = padding

        self.text = self.font.render(
            self.text_input, True, self.base_color
        ).convert_alpha()

        if self.image is None:
            self.image = self.text

        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self._update_text_rect()

    def _update_text_rect(self):
        if self.text_align == "right":
            self.text_rect = self.text.get_rect(
                midright=(self.rect.right - self.padding, self.rect.centery)
            )
        elif self.text_align == "left":
            self.text_rect = self.text.get_rect(
                midleft=(self.rect.left + self.padding, self.rect.centery)
            )
        else:
            self.text_rect = self.text.get_rect(center=self.rect.center)

    def update(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position):
        return self.rect.collidepoint(position)

    def changeColor(self, position):
        if self.checkForInput(position):
            self.text = self.font.render(
                self.text_input, True, self.hovering_color
            ).convert_alpha()
        else:
            self.text = self.font.render(
                self.text_input, True, self.base_color
            ).convert_alpha()

        self._update_text_rect()


class GameMenu:
    def __init__(self):
        pygame.init()

        self.screen = config.screen
        self.screen_size = config.screen_size
        pygame.display.set_caption("Your Only Move is Fight")

        self.bg = pygame.image.load(config.resource_path("assets/BG_1.png")).convert()
        self.bg = pygame.transform.smoothscale(self.bg, self.screen_size)

        self.x_pos = self.screen_size[0] - self.screen_size[0] * 0.8
        self.clock = pygame.time.Clock()

        self.state = "main_menu"
        self.game_mode = None
        self.server_ip = None
        self.local_ip = None

        self.text_input = ""
        self.input_active = False

    def get_font(self, size):
        return pygame.font.Font(config.resource_path("assets/GochiHand-Regular.ttf"), size)

    def get_local_ip(self):
        """Get the local IP address of the machine."""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def draw_main_menu(self):
        """Draw main menu screen."""
        self.screen.blit(self.bg, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        title_rect = self.get_font(100).render(
            "Your Only Move is Fight", True, "#ecad00"
        )
        title_main = self.get_font(98).render("Your Only Move is Fight", True, "#ec4300")

        out_rect = title_rect.get_rect(center=(640, 100))
        main_rect = title_main.get_rect(center=out_rect.center)

        self.screen.blit(title_rect, out_rect)
        self.screen.blit(title_main, main_rect)

        play_button = Button(
            image=pygame.image.load(config.resource_path("assets/MenuBox.png")),
            pos=(self.x_pos, 250),
            text_input="PLAY        ",
            font=self.get_font(75),
            base_color="#ffffff",
            hovering_color="Orange",
        )

        quit_button = Button(
            image=pygame.image.load(config.resource_path("assets/MenuBox.png")),
            pos=(self.x_pos, 550),
            text_input="QUIT         ",
            font=self.get_font(70),
            base_color="#ffffff",
            hovering_color="Orange",
        )

        for button in [play_button, quit_button]:
            button.changeColor(mouse_pos)
            button.update(self.screen)

        return play_button, quit_button

    def draw_play_menu(self):
        """Draw play mode selection screen."""
        self.screen.blit(self.bg, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        title = self.get_font(100).render("CONNECT TO GAME", True, "Red")
        title_rect = title.get_rect(center=(640, 100))
        self.screen.blit(title, title_rect)

        lan_button = Button(
            image=pygame.image.load(config.resource_path("assets/MenuBox.png")),
            pos=(self.x_pos, 250),
            text_input="Play LAN  ",
            font=self.get_font(70),
            base_color="#ffffff",
            hovering_color="Orange",
        )

        online_button = Button(
            image=pygame.image.load(config.resource_path("assets/MenuBox.png")),
            pos=(self.x_pos, 370),
            text_input="Online      ",
            font=self.get_font(70),
            base_color="#ffffff",
            hovering_color="Orange",
        )
        solo_button = Button(
                image=pygame.image.load(config.resource_path("assets/MenuBox.png")),
                pos=(self.x_pos, 490),
                text_input ="Solo         ",
                font=self.get_font(70),
                base_color="#ffffff",
                hovering_color="Orange",
        )
        train_button = Button(
                image=pygame.image.load(config.resource_path("assets/MenuBox.png")),
                pos=(self.x_pos, 610),
                text_input ="Training         ",
                font=self.get_font(70),
                base_color="#ffffff",
                hovering_color="Orange",
        )
        
        back_button = Button(
            image=pygame.image.load(config.resource_path("assets/MenuBox.png")),
            pos=(self.x_pos, 730),
            text_input="BACK         ",
            font=self.get_font(70),
            base_color="#000000",
            hovering_color="Orange",
        )

        for button in [lan_button, online_button,  solo_button, train_button , back_button]:
            button.changeColor(mouse_pos)
            button.update(self.screen)

        return lan_button, online_button,solo_button, train_button, back_button

    def draw_difficulty_menu(self):
        """Draw difficulty solo mode selection screen."""
        self.screen.blit(self.bg, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        title = self.get_font(100).render("DIFFICULTY", True, "Red")
        title_rect = title.get_rect(center=(640, 100))
        self.screen.blit(title, title_rect)
        easy_button = Button(
                image = pygame.image.load(config.resource_path("assets/MenuBox.png")),
                pos = (self.x_pos,250),
                text_input = "Easy          ",
                font = self.get_font(70),
                base_color= "#ffffff",
                hovering_color = "Orange",
            )
        medium_button = Button(
                image = pygame.image.load(config.resource_path("assets/MenuBox.png")),
                pos = (self.x_pos,400),
                text_input = "Medium        ",
                font = self.get_font(70),
                base_color= "#ffffff",
                hovering_color = "Orange",
            )
        hard_button = Button(
                image = pygame.image.load(config.resource_path("assets/MenuBox.png")),
                pos = (self.x_pos,550),
                text_input = "Hard          ",
                font = self.get_font(70),
                base_color= "#ffffff",
                hovering_color = "Orange",
            )
        back_button = Button(
                image = pygame.image.load(config.resource_path("assets/MenuBox.png")),
                pos = (self.x_pos, 700),
                text_input = "BACK          ",
                font = self.get_font(70),
                base_color = "#000000",
                hovering_color = "Orange"
            )

        for button in [easy_button, medium_button, hard_button, back_button]:
            button.changeColor(mouse_pos)
            button.update(self.screen)
        return easy_button, medium_button, hard_button, back_button



    def draw_lan_setup(self):
        """Draw LAN setup screen (host or join)."""
        self.screen.blit(self.bg, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        title = self.get_font(80).render("LAN SETUP", True, "Red")
        title_rect = title.get_rect(center=(640, 80))
        self.screen.blit(title, title_rect)

        host_button = Button(
            image=pygame.image.load(config.resource_path("assets/MenuBox.png")),
            pos=(self.x_pos, 250),
            text_input="Host Server",
            font=self.get_font(70),
            base_color="#ffffff",
            hovering_color="Orange",
        )

        join_button = Button(
            image=pygame.image.load(config.resource_path("assets/MenuBox.png")),
            pos=(self.x_pos, 400),
            text_input="Join Game   ",
            font=self.get_font(70),
            base_color="#ffffff",
            hovering_color="Orange",
        )

        back_button = Button(
            image=pygame.image.load(config.resource_path("assets/MenuBox.png")),
            pos=(self.x_pos, 550),
            text_input="BACK         ",
            font=self.get_font(70),
            base_color="#000000",
            hovering_color="Orange",
        )

        for button in [host_button, join_button, back_button]:
            button.changeColor(mouse_pos)
            button.update(self.screen)

        return host_button, join_button, back_button

    def draw_lan_host_info(self):
        """Draw screen showing host info."""
        self.screen.blit(self.bg, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        title = self.get_font(70).render("SERVER HOSTING", True, "Green")
        title_rect = title.get_rect(center=(640, 80))
        self.screen.blit(title, title_rect)

        info_text = self.get_font(50).render(
            f"Your IP: {self.local_ip}", True, "#ffffff"
        )
        info_rect = info_text.get_rect(center=(640, 250))
        self.screen.blit(info_text, info_rect)

        instruction = self.get_font(40).render(
            "Share this IP with your friend", True, "#ecad00"
        )
        instruction_rect = instruction.get_rect(center=(640, 350))
        self.screen.blit(instruction, instruction_rect)

        start_button = Button(
            image=pygame.image.load(config.resource_path("assets/MenuBox.png")),
            pos=(self.x_pos, 480),
            text_input="START SERVER",
            font=self.get_font(60),
            base_color="#ffffff",
            hovering_color="Orange",
        )

        back_button = Button(
            image=pygame.image.load(config.resource_path("assets/MenuBox.png")),
            pos=(self.x_pos, 600),
            text_input="BACK         ",
            font=self.get_font(50),
            base_color="#000000",
            hovering_color="Orange",
        )

        for button in [start_button, back_button]:
            button.changeColor(mouse_pos)
            button.update(self.screen)

        return start_button, back_button

    def draw_lan_join(self):
        """Draw LAN join screen with IP input."""
        self.screen.blit(self.bg, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        title = self.get_font(70).render("JOIN GAME", True, "Blue")
        title_rect = title.get_rect(center=(640, 80))
        self.screen.blit(title, title_rect)

        instruction = self.get_font(40).render("Enter Server IP:", True, "#ffffff")
        instruction_rect = instruction.get_rect(center=(640, 200))
        self.screen.blit(instruction, instruction_rect)

        input_box = pygame.Rect(400, 280, 400, 60)
        color = (255, 165, 0) if self.input_active else (100, 100, 100)
        pygame.draw.rect(self.screen, color, input_box, 3)

        text_surface = self.get_font(40).render(self.text_input, True, "#ffffff")
        self.screen.blit(text_surface, (input_box.x + 10, input_box.y + 10))

        join_button = Button(
            image=pygame.image.load(config.resource_path("assets/MenuBox.png")),
            pos=(self.x_pos, 480),
            text_input="JOIN SERVER  ",
            font=self.get_font(60),
            base_color="#ffffff",
            hovering_color="Orange",
        )

        back_button = Button(
            image=pygame.image.load(config.resource_path("assets/MenuBox.png")),
            pos=(self.x_pos, 600),
            text_input="BACK         ",
            font=self.get_font(50),
            base_color="#000000",
            hovering_color="Orange",
        )

        for button in [join_button, back_button]:
            button.changeColor(mouse_pos)
            button.update(self.screen)

        return input_box, join_button, back_button

    def run(self):
        """Main menu loop - returns (game_mode, server_ip) when user selects to play."""
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            if self.state == "main_menu":
                play_btn, quit_btn = self.draw_main_menu()
    def draw_lan_join(self):
        """Draw LAN join screen with IP input."""
        self.screen.blit(self.bg, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        title = self.get_font(70).render("JOIN GAME", True, "Blue")
        title_rect = title.get_rect(center=(640, 80))
        self.screen.blit(title, title_rect)

        instruction = self.get_font(40).render("Enter Server IP:", True, "#ffffff")
        instruction_rect = instruction.get_rect(center=(640, 200))
        self.screen.blit(instruction, instruction_rect)

        input_box = pygame.Rect(400, 280, 400, 60)
        color = (255, 165, 0) if self.input_active else (100, 100, 100)
        pygame.draw.rect(self.screen, color, input_box, 3)

        text_surface = self.get_font(40).render(self.text_input, True, "#ffffff")
        self.screen.blit(text_surface, (input_box.x + 10, input_box.y + 10))

        join_button = Button(
            image=pygame.image.load(config.resource_path("assets/MenuBox.png")),
            pos=(self.x_pos, 480),
            text_input="JOIN SERVER  ",
            font=self.get_font(60),
            base_color="#ffffff",
            hovering_color="Orange",
        )

        back_button = Button(
            image=pygame.image.load(config.resource_path("assets/MenuBox.png")),
            pos=(self.x_pos, 600),
            text_input="BACK         ",
            font=self.get_font(50),
            base_color="#000000",
            hovering_color="Orange",
        )

        for button in [join_button, back_button]:
            button.changeColor(mouse_pos)
            button.update(self.screen)

        return input_box, join_button, back_button

    def run(self):
        """Main menu loop - returns (game_mode, server_ip) when user selects to play."""
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            if self.state == "main_menu":
                play_btn, quit_btn = self.draw_main_menu()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if play_btn.checkForInput(mouse_pos):
                            button_select_sound.play()
                            self.state = "play_menu"
                        if quit_btn.checkForInput(mouse_pos):
                            pygame.quit()
                            sys.exit()

            elif self.state == "play_menu":
                lan_btn, online_btn,solo_button, train_button ,back_btn = self.draw_play_menu()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        button_select_sound.play()
                        if lan_btn.checkForInput(mouse_pos):
                            self.local_ip = self.get_local_ip()
                            self.state = "lan_setup"
                        if online_btn.checkForInput(mouse_pos):
                            if (mixer_initialized):
                                pygame.mixer.music.fadeout(1000)
                            self.game_mode = "online"
                            self.server_ip = "89.168.39.144"
                            running = False
                        if solo_button.checkForInput(mouse_pos):
                            self.state = "difficulty"
                        if train_button.checkForInput(mouse_pos):
                            self.game_mode = "train"
                            running = False
                        elif back_btn.checkForInput(mouse_pos):
                            self.state = "main_menu"
                            

            elif self.state == "lan_setup":
                host_btn, join_btn, back_btn = self.draw_lan_setup()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        button_select_sound.play()
                        if host_btn.checkForInput(mouse_pos): 
                            self.state = "lan_host_info"
                        if join_btn.checkForInput(mouse_pos):
                            self.state = "lan_join"
                            self.text_input = ""
                            self.input_active = True     
                        if back_btn.checkForInput(mouse_pos):
                            self.state = "play_menu"
                            
            elif self.state == "lan_host_info":
                start_btn, back_btn = self.draw_lan_host_info()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        button_select_sound.play()
                        if start_btn.checkForInput(mouse_pos):
                            if (mixer_initialized):
                                pygame.mixer.music.fadeout(1000)
                            self.game_mode = "lan_host"
                            self.server_ip = self.local_ip
                            running = False
                        if back_btn.checkForInput(mouse_pos):
                            self.state = "lan_setup"

            elif self.state == "lan_join":
                input_box, join_btn, back_btn = self.draw_lan_join()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if input_box.collidepoint(mouse_pos):
                            self.input_active = True
                        else:
                            self.input_active = False

                        if join_btn.checkForInput(mouse_pos) and self.text_input: 
                            if (mixer_initialized):
                                pygame.mixer.music.fadeout(1000)
                            button_select_sound.play()    
                            self.game_mode = "lan_client"
                            self.server_ip = self.text_input
                            running = False
                            
                        if back_btn.checkForInput(mouse_pos):
                            button_select_sound.play()
                            self.state = "lan_setup"
                            self.input_active = False

                    if event.type == pygame.KEYDOWN:
                        if self.input_active: 
                            if event.key == pygame.K_BACKSPACE:
                                self.text_input = self.text_input[:-1]
                            elif event.key == pygame.K_RETURN:
                                
                                if self.text_input:
                                    self.game_mode = "lan_client"
                                    self.server_ip = self.text_input
                                    running = False
                            else:
                                self.text_input += event.unicode
                                
            elif self.state == "difficulty":
                easy_btn, medium_btn, hard_btn, back_btn = self.draw_difficulty_menu()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if easy_btn.checkForInput(mouse_pos):
                            self.game_mode = "solo"
                            self.server_ip = "easy"
                            running = False
                        if medium_btn.checkForInput(mouse_pos):
                            self.game_mode = "solo"
                            self.server_ip = "medium"
                            running = False
                        if hard_btn.checkForInput(mouse_pos):
                            self.game_mode = "solo"
                            self.server_ip = "hard"
                            running = False
                        if back_btn.checkForInput(mouse_pos):
                            self.state = "play_menu"

            pygame.display.update()
            self.clock.tick(60)

        return self.game_mode, self.server_ip
