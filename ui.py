import math
import random

import pygame

import config

COLORS = {
    "panel_bg": (89, 52, 30),
    "panel_border": (51, 30, 17),
    "panel_highlight": (140, 85, 50),
    "text_shadow": (51, 30, 17),
    "name_color": (255, 230, 180),
    "bar_bg": (30, 30, 30),
    "bar_border": (60, 40, 25),
}


def get_bar_color(fill_ratio):
    ratio = min(1.0, fill_ratio)

    if ratio < 0.33:
        t = ratio / 0.33
        r = int(100 + 155 * t)
        g = 255
        b = int(100 * (1 - t))
    elif ratio < 0.66:
        t = (ratio - 0.33) / 0.33
        r = 255
        g = int(255 - 70 * t)
        b = 0
    else:
        t = (ratio - 0.66) / 0.34
        r = 255
        g = int(185 - 130 * t)
        b = 0

    return (min(255, r), max(0, min(255, g)), max(0, b))


class Stock:
    RADIUS = 8
    SPACING = 24
    ALIVE_COLOR = (255, 200, 60)
    ALIVE_BORDER = (200, 150, 30)
    DEAD_COLOR = (50, 35, 20)
    DEAD_BORDER = (70, 50, 30)

    def __init__(self, index, anchor_x, anchor_y):
        self.x = anchor_x + index * self.SPACING
        self.y = anchor_y
        self.alive = True

    def draw(self, surface, offset=(0, 0)):
        dx = int(self.x + offset[0])
        dy = int(self.y + offset[1])
        if self.alive:
            pygame.draw.circle(surface, self.ALIVE_COLOR, (dx, dy), self.RADIUS)
            pygame.draw.circle(surface, self.ALIVE_BORDER, (dx, dy), self.RADIUS, 2)
        else:
            pygame.draw.circle(surface, self.DEAD_COLOR, (dx, dy), self.RADIUS)
            pygame.draw.circle(surface, self.DEAD_BORDER, (dx, dy), self.RADIUS, 2)


class StockDisplay:
    """Row of Stock circles for one player."""

    def __init__(self, total, anchor_x, anchor_y):
        self.stocks = [Stock(i, anchor_x, anchor_y) for i in range(total)]

    def set_stocks(self, count):
        for i, s in enumerate(self.stocks):
            s.alive = i < count

    def draw(self, surface, offset=(0, 0)):
        for s in self.stocks:
            s.draw(surface, offset)


class Bubble:
    def __init__(self, x, bar_top, bar_height):
        self.x = x + random.randint(-5, 5)
        self.y = bar_top + bar_height
        self.target_y = bar_top - random.randint(5, 20)
        self.radius = random.randint(3, 8)
        self.speed = random.uniform(1.5, 3.5)
        self.wobble_offset = random.uniform(0, math.pi * 2)
        self.wobble_speed = random.uniform(3, 6)
        self.alpha = 255
        self.alive = True

    def update(self):
        self.y -= self.speed
        self.x += (
            math.sin(
                pygame.time.get_ticks() * 0.01 * self.wobble_speed + self.wobble_offset
            )
            * 0.5
        )
        if self.y < self.target_y:
            self.alpha -= 15
            self.radius = max(1, self.radius - 0.3)
            if self.alpha <= 0:
                self.alive = False

    def draw(self, surface, color):
        if self.alive and self.radius > 0:
            bubble_color = (
                min(255, color[0] + 50),
                min(255, color[1] + 50),
                min(255, color[2] + 50),
            )
            pygame.draw.circle(
                surface, bubble_color, (int(self.x), int(self.y)), int(self.radius)
            )
            if self.radius > 3:
                highlight_pos = (
                    int(self.x - self.radius * 0.3),
                    int(self.y - self.radius * 0.3),
                )
                pygame.draw.circle(
                    surface,
                    (255, 255, 255),
                    highlight_pos,
                    max(1, int(self.radius * 0.3)),
                )


class Drip:
    def __init__(self, x, bar_bottom):
        self.x = x
        self.y = bar_bottom
        self.length = random.randint(5, 15)
        self.max_length = random.randint(20, 40)
        self.width = random.randint(3, 6)
        self.grow_speed = random.uniform(0.3, 0.8)
        self.drip_speed = 0
        self.detached = False
        self.drop_y = 0
        self.alive = True

    def update(self):
        if not self.detached:
            self.length += self.grow_speed
            if self.length >= self.max_length:
                self.detached = True
                self.drop_y = self.y + self.length
        else:
            self.drip_speed += 0.5
            self.drop_y += self.drip_speed
            if self.drop_y > self.y + 100:
                self.alive = False

    def draw(self, surface, color):
        if not self.alive:
            return
        if not self.detached:
            points = [
                (self.x - self.width // 2, self.y),
                (self.x + self.width // 2, self.y),
                (self.x + self.width // 4, self.y + self.length * 0.7),
                (self.x, self.y + self.length),
                (self.x - self.width // 4, self.y + self.length * 0.7),
            ]
            pygame.draw.polygon(surface, color, points)
        else:
            pygame.draw.circle(
                surface, color, (int(self.x), int(self.drop_y)), self.width // 2
            )


class PercentageBar:
    def __init__(self, player_num, name, position, total_stocks=3):
        self.player_num = player_num
        self.name = name
        self.position = position
        self.percentage = 0
        self.display_percentage = 0

        self.width = 250
        self.height = 115
        self.border_width = 3

        self.bar_margin = 15
        self.bar_height = 25
        self.bar_width = self.width - 2 * self.bar_margin

        screen_w, screen_h = config.screen.get_size()
        margin = 40

        if position == 1:
            self.x = margin
        if position == 2:
            self.x = (screen_w / 2) - margin - self.width
        if position == 3:
            self.x = (screen_w / 2) + margin
        if position == 4:
            self.x = screen_w - self.width - margin

        self.y = screen_h - self.height - 30

        self.bar_x = self.x + self.bar_margin
        self.bar_y = self.y + 55

        stock_anchor_x = int(self.x + self.bar_margin + 12)
        stock_anchor_y = int(self.bar_y + self.bar_height + 14)
        self.stock_display = StockDisplay(total_stocks, stock_anchor_x, stock_anchor_y)

        self.bubbles = []
        self.drips = []
        self.shake_offset = [0, 0]
        self.last_bubble_time = 0
        self.last_drip_time = 0

        self.name_font = pygame.font.Font(config.resource_path("assets/GochiHand-Regular.ttf"), 32)
        self.percent_font = pygame.font.Font(config.resource_path("assets/GochiHand-Regular.ttf"), 48)

    def update(self, percentage):
        adj = 1 / (0.8 + len(str(int(self.display_percentage))) * 0.2) 

        self.percentage = max(0, percentage)
        self.percent_font = pygame.font.Font(config.resource_path("assets/GochiHand-Regular.ttf"), round(48 * adj))
        diff = self.percentage - self.display_percentage
        self.display_percentage += diff * 0.15
        fill_ratio = self.display_percentage / 100.0

        if fill_ratio >= 1.0:
            overflow = fill_ratio - 1.0
            shake_intensity = min(8, 2 + overflow * 10)
            self.shake_offset[0] = random.uniform(-shake_intensity, shake_intensity)
            self.shake_offset[1] = random.uniform(
                -shake_intensity * 0.5, shake_intensity * 0.5
            )

            current_time = pygame.time.get_ticks()
            bubble_interval = max(50, 200 - overflow * 100)
            if current_time - self.last_bubble_time > bubble_interval:
                bubble_x = self.bar_x + random.randint(10, int(self.bar_width) - 10)
                self.bubbles.append(Bubble(bubble_x, self.bar_y, self.bar_height))
                self.last_bubble_time = current_time

            if overflow > 0.3:
                drip_interval = max(100, 500 - overflow * 200)
                if current_time - self.last_drip_time > drip_interval:
                    drip_x = self.bar_x + random.randint(10, int(self.bar_width) - 10)
                    self.drips.append(Drip(drip_x, self.bar_y + self.bar_height))
                    self.last_drip_time = current_time
        else:
            self.shake_offset = [0, 0]

        for bubble in self.bubbles[:]:
            bubble.update()
            if not bubble.alive:
                self.bubbles.remove(bubble)

        for drip in self.drips[:]:
            drip.update()
            if not drip.alive:
                self.drips.remove(drip)

    def set_stocks(self, count):
        self.stock_display.set_stocks(count)

    def draw(self, screen):
        draw_x = self.x + self.shake_offset[0]
        draw_y = self.y + self.shake_offset[1]
        bar_draw_x = self.bar_x + self.shake_offset[0]
        bar_draw_y = self.bar_y + self.shake_offset[1]

        fill_ratio = self.display_percentage / 100.0
        bar_color = get_bar_color(fill_ratio)

        panel_rect = pygame.Rect(draw_x, draw_y, self.width, self.height)
        pygame.draw.rect(screen, COLORS["panel_bg"], panel_rect, border_radius=10)
        pygame.draw.rect(
            screen, COLORS["panel_border"], panel_rect, 3, border_radius=10
        )

        name_text = self.name_font.render(self.name, True, COLORS["name_color"])
        name_shadow = self.name_font.render(self.name, True, COLORS["text_shadow"])
        name_x = draw_x + self.width * 1 / 3 - name_text.get_width() * 1 / 4
        screen.blit(name_shadow, (name_x - 29, draw_y + 10 + 1))
        screen.blit(name_text, (name_x - 30, draw_y + 10))

        percent_str = f"{int(self.display_percentage)}%"
        percent_color = (
            bar_color
            if fill_ratio < 1.0
            else (
                255,
                min(
                    255, int(100 + 155 * abs(math.sin(pygame.time.get_ticks() * 0.01)))
                ),
                100,
            )
        )
        percent_text = self.percent_font.render(percent_str, True, percent_color)
        percent_shadow = self.percent_font.render(
            percent_str, True, COLORS["text_shadow"]
        )
        percent_x = draw_x + self.width - percent_text.get_width() - 15
        percent_y = draw_y
        screen.blit(percent_shadow, (percent_x + 2, percent_y + 2))
        screen.blit(percent_text, (percent_x, percent_y))

        bar_bg_rect = pygame.Rect(
            bar_draw_x - 2, bar_draw_y - 2, self.bar_width + 4, self.bar_height + 4
        )
        pygame.draw.rect(screen, COLORS["bar_border"], bar_bg_rect, border_radius=5)
        inner_bg_rect = pygame.Rect(
            bar_draw_x, bar_draw_y, self.bar_width, self.bar_height
        )
        pygame.draw.rect(screen, COLORS["bar_bg"], inner_bg_rect, border_radius=3)

        fill_width = min(self.bar_width, self.bar_width * fill_ratio)
        if fill_width > 0:
            if fill_ratio >= 1.0:
                self._draw_wavy_bar(
                    screen, bar_draw_x, bar_draw_y, fill_width, bar_color
                )
            else:
                self._draw_gradient_bar(
                    screen, bar_draw_x, bar_draw_y, fill_width, fill_ratio
                )

        for bubble in self.bubbles:
            bubble.draw(screen, bar_color)
        for drip in self.drips:
            drip.draw(screen, bar_color)

        self.stock_display.draw(screen, self.shake_offset)

    def _draw_gradient_bar(self, screen, x, y, width, fill_ratio):
        if width <= 0:
            return
        segments = max(1, int(width / 4))
        segment_width = width / segments
        for i in range(segments):
            segment_x = x + i * segment_width
            segment_ratio = (i / segments) * fill_ratio
            color = get_bar_color(segment_ratio)
            rect = pygame.Rect(segment_x, y + 2, segment_width + 1, self.bar_height - 4)
            pygame.draw.rect(screen, color, rect)
        highlight_rect = pygame.Rect(x + 2, y + 3, width - 4, 4)
        highlight_color = (
            min(255, get_bar_color(fill_ratio)[0] + 60),
            min(255, get_bar_color(fill_ratio)[1] + 60),
            min(255, get_bar_color(fill_ratio)[2] + 60),
        )
        pygame.draw.rect(screen, highlight_color, highlight_rect, border_radius=2)

    def _draw_wavy_bar(self, screen, x, y, width, color):
        time = pygame.time.get_ticks() * 0.005
        overflow = (self.display_percentage / 100.0) - 1.0
        wave_intensity = min(4, 1 + overflow * 5)
        slice_height = 2
        num_slices = self.bar_height // slice_height
        for i in range(num_slices):
            slice_y = y + i * slice_height
            wave_offset = math.sin(time * 3 + i * 0.5) * wave_intensity
            color_var = int(math.sin(time * 5 + i * 0.3) * 20)
            slice_color = (
                min(255, max(0, color[0] + color_var)),
                min(255, max(0, color[1] - abs(color_var))),
                min(255, max(0, color[2])),
            )
            rect = pygame.Rect(x + wave_offset, slice_y + 2, width, slice_height)
            pygame.draw.rect(screen, slice_color, rect)
        highlight_rect = pygame.Rect(x + 2, y + 3, width - 4, 4)
        pygame.draw.rect(screen, (255, 200, 150), highlight_rect, border_radius=2)


class DamageDisplay:
    def __init__(self):
        self.bars = {}

    def add_player(self, player_id, name, position, total_stocks=3):
        self.bars[player_id] = PercentageBar(
            player_id, name, position, total_stocks=total_stocks
        )

    def update(self, player_id, percentage):
        if player_id in self.bars:
            self.bars[player_id].update(percentage)

    def set_stocks(self, player_id, count):
        if player_id in self.bars:
            self.bars[player_id].set_stocks(count)

    def draw(self, screen):
        for bar in self.bars.values():
            bar.draw(screen)

class RoundTimer:
    def __init__(self):
        screen_w, screen_h = config.screen.get_size()
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.font = pygame.font.Font(config.resource_path("assets/GochiHand-Regular.ttf"), 32)

    def draw(self, screen, timer):
        if (timer % 60) < 10:
            text_shadow = self.font.render(f"0{timer}", True, (40, 0, 0))
            text = self.font.render(f"0{timer}", True, (255, 255, 255))
        else:
            text_shadow = self.font.render(f"{timer}", True, (40, 0, 0))
            text = self.font.render(f"{timer}", True, (255, 255, 255))

        tx = (self.screen_w - text.get_width()) / 2
        ty = (self.screen_h - text.get_height()) / 30

        screen.blit(text_shadow, (tx + 2, ty + 2))
        screen.blit(text, (tx, ty))

class DeathUI:
    def __init__(self):
        self.text = "KNOCKOUT !"
        screen_w, screen_h = config.screen.get_size()
        self.screen_w = screen_w
        self.screen_h = screen_h

        # Horizontal band
        self.band_height = 120
        self.band_y = (screen_h - self.band_height) / 2

        self.band = pygame.Surface((screen_w, self.band_height))
        self.band.fill((0, 0, 0))
        self.band.set_alpha(180)

        # Red tint on the band
        self.red_tint = pygame.Surface((screen_w, self.band_height))
        self.red_tint.fill((80, 0, 0))
        self.red_tint.set_alpha(40)

        # Big bold font
        self.font = pygame.font.Font(config.resource_path("assets/GochiHand-Regular.ttf"), 120)
        self.font2 = pygame.font.Font(config.resource_path("assets/GochiHand-Regular.ttf"), 32)

    def draw(self, screen, winner, roundtime):
        # Dark band
        screen.blit(self.band, (0, self.band_y))
        # Red tint
        screen.blit(self.red_tint, (0, self.band_y))

        # Shadow
        shadow = self.font.render(self.text, True, (40, 0, 0))
        sx = (self.screen_w - shadow.get_width()) / 2 + 3
        sy = (self.screen_h - shadow.get_height()) / 2 + 3
        screen.blit(shadow, (sx, sy))

        # Main text
        text = self.font.render(self.text, True, (180, 20, 20))
        winner_text = self.font2.render(f"Winner: {winner}", True, (255, 255, 255))
        if roundtime< 10:
            time_text = self.font2.render(f"Round lasted: {math.floor(roundtime / 60)}:0{round(roundtime)}", True, (255, 255, 255))
            time_shadow = self.font2.render(f"Round lasted: {math.floor(roundtime / 60)}:0{round(roundtime)}", True, (40, 0, 0))
        else:
            time_text = self.font2.render(f"Round lasted: {math.floor(roundtime / 60)}:{round(roundtime % 60)}", True, (255, 255, 255))
            time_shadow = self.font2.render(f"Round lasted: {math.floor(roundtime / 60)}:{round(roundtime % 60)}", True, (40, 0, 0))

        tx = (self.screen_w - text.get_width()) / 2
        ty = (self.screen_h - text.get_height()) / 2
        wx = (self.screen_w - winner_text.get_width()) / 2
        wy = ty + text.get_height() + 5
        rx = (self.screen_w - winner_text.get_width()) / 2
        ry = ty + text.get_height() + 50

        winner_text = self.font2.render(f"Winner: {winner}", True, (255, 255, 255))
        winner_shadow = self.font2.render(f"Winner: {winner}", True, (40, 0, 0))

        screen.blit(winner_shadow, (wx + 2, wy + 2))
        screen.blit(time_shadow, (rx + 2, ry + 2))
        screen.blit(text, (tx, ty))
        screen.blit(winner_text, (wx, wy))
        screen.blit(time_text, (rx, ry))

class KeyGuide:
    def __init__(self):
        return
        #self.keyguidepc = pygame.image.load(config.resource_path("assets/keyguidepc.png")).convert_alpha()
        #self.keyguidepc.set_alpha(184)
        #screen_w, screen_h = config.screen.get_size()
        #self.screen_w = screen_w
        #self.screen_h = screen_h
    
    def drawkeyguidepc(self,screen):
        return
        #screen.blit(self.keyguidepc,(self.screen_w * 3/4, self.screen_h / 1.825 - self.keyguidepc.get_size()[1]))

class PlayerPointer:
    def __init__(self):
        self.sprite = pygame.image.load(config.resource_path("assets/triangle.png"))
        self.imagerect = self.sprite.get_rect()
        self.posx = 0
        screen_w, screen_h = config.screen.get_size()
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.posy = screen_h
        self.is_active = False

    def draw(self,screen,player):
            self.posx = player.position[0]
            self.posy = self.screen_h * 1/100
            screen.blit(self.sprite, (self.posx,self.posy))

    def track(self,screen,player):
        if player.position[1] < 0:
            self.draw(screen,player)
