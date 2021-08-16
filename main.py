import pygame as pg
import os
from pg_funcs import *
import shelve
import json


# Globals
GAME_CAPTION = "Tower Defense"
TILE_SIZE = 64


class Enemy:
    def __init__(self, health, speed, pos, enemy_map):
        self.health = health
        self.speed = speed
        self.enemy_map = enemy_map
        self.money = 1
        self.radius = 15
        self.pos = (int(-TILE_SIZE*pos), int(6.5*TILE_SIZE))
        self.velocity = (1, 0)
        self.enemy_map_index = 0
        self.next_check = (self.enemy_map[self.enemy_map_index][1]*TILE_SIZE+32,
                           self.enemy_map[self.enemy_map_index][0]*TILE_SIZE+32)
        self.dead = False
        self.finished = False

    def draw(self, window):
        pg.draw.circle(window, pg.color.Color('red'), self.pos, self.radius)

    def move(self):
        self.pos = (self.pos[0] + (self.velocity[0] * self.speed), self.pos[1] + (self.velocity[1] * self.speed))
        if self.pos == self.next_check:
            self.enemy_map_index += 1
            if self.enemy_map_index != len(self.enemy_map):
                self.next_check = (self.enemy_map[self.enemy_map_index][1]*TILE_SIZE+32,
                                   self.enemy_map[self.enemy_map_index][0]*TILE_SIZE+32)
                self.velocity = (self.enemy_map[self.enemy_map_index][1]-self.enemy_map[self.enemy_map_index-1][1],
                                 self.enemy_map[self.enemy_map_index][0]-self.enemy_map[self.enemy_map_index-1][0])
            else:
                pass
        elif self.enemy_map_index == len(self.enemy_map):
            if -self.radius > self.pos[0] or self.pos[0] > self.radius + 960 or\
                    -self.radius > self.pos[1] or self.pos[1] > self.radius + 960:
                self.finished = True

    def check_state(self):
        if self.health <= 0:
            self.dead = True
        else:
            self.move()


class NewRound:
    def __init__(self, number, enemy_map):
        self.number = number
        self.enemy_map = enemy_map
        self.enemies = []
        self.generate()
        self.started = False
        self.ended = False

    def generate(self):
        for enemy in range(self.number+3):
            self.enemies.append(Enemy(1, 4, len(self.enemies), self.enemy_map))

    def check_state(self, player):
        if len(self.enemies) == 0:
            self.ended = True
        for enemy in self.enemies.copy():
            if enemy.dead:
                self.enemies.remove(enemy)
                player['money'] += enemy.money
            elif enemy.finished:
                player['lives'] -= 1
                self.enemies.remove(enemy)
            else:
                enemy.check_state()


class GenericScene:
    def __init__(self):
        self.command = None

    def draw(self, window):
        pass

    def run(self):
        pass

    def reset(self):
        self.command = None

    def check_event(self, event):
        pass


class MainMenu(GenericScene):
    def __init__(self):
        GenericScene.__init__(self)
        self.menu_buttons = [
            create_button((150, 150), (300, 100), text="Play", font=FONTS['MEDIUM']),
            create_button((150, 400), (300, 100), text="Options", font=FONTS['MEDIUM']),
        ]
        self.commands = [
            'map', 'options'
        ]

    def check_event(self, event):
        if event.type == pg.MOUSEBUTTONUP:
            if event.button == 1:
                x, y = get_mouse()
                for button, command in zip(self.menu_buttons, self.commands):
                    if button[0][0].collidepoint(x, y):
                        self.command = command

    def draw(self, window):
        window.fill(pg.color.Color('black'))
        for button in self.menu_buttons:
            window.fill(button[0][1], button[0][0])
            blit_text_object(window, button[1])


class PauseMenu(GenericScene):
    def __init__(self):
        GenericScene.__init__(self)
        pass


class Options(GenericScene):
    def __init__(self):
        GenericScene.__init__(self)
        self.menu_buttons = [
            create_button((150, 150), (300, 100), text="Back To Main", font=FONTS['MEDIUM']),
            create_button((150, 400), (300, 100), text="Options", font=FONTS['MEDIUM']),
        ]
        self.commands = [
            'main_menu', None
        ]

    def check_event(self, event):
        if event.type == pg.MOUSEBUTTONUP:
            if event.button == 1:
                x, y = get_mouse()
                for button, command in zip(self.menu_buttons, self.commands):
                    if button[0][0].collidepoint(x, y):
                        self.command = command

    def draw(self, window):
        window.fill(pg.color.Color('black'))
        for button in self.menu_buttons:
            window.fill(button[0][1], button[0][0])
            blit_text_object(window, button[1])


class Game(GenericScene):
    def __init__(self):
        GenericScene.__init__(self)
        self.player = {"money": 500, "lives": 10}
        self.map = [[0] * (pg.display.Info().current_w // TILE_SIZE)] * (pg.display.Info().current_w // TILE_SIZE)
        self.map_colors = [pg.color.Color('gray19'), pg.color.Color('steelblue')]
        self.map_start = (0, 0)
        self.map_direction = (0, 1)
        self.enemy_map = []
        self.choose_level()
        self.create_enemy_map()
        self.round_number = 1
        self.menu_buttons = [
            create_button((960, 0), (256, 100), text="Towers", font=FONTS['MEDIUM'],
                          text_color=pg.color.Color('gold')),
            create_button((0, 0), (300, 50), text=f"Lives: {self.player['lives']}",
                          font=FONTS['SMALL'],text_color=pg.color.Color('gold')),
            create_button((300, 0), (300, 50), text=f"${self.player['money']}",
                          font=FONTS['SMALL'], text_color=pg.color.Color('gold')),
        ]
        self.current_round = NewRound(self.round_number, self.enemy_map)

    def choose_level(self):
        """Generate tile map here (integer representation of enemy path + obstacles)"""
        with open('static/levels.json', 'r') as f:
            self.map = json.load(f)['name']
        self.map_start = (6, 0)
        self.map_direction = (0, 1)

    def create_enemy_map(self):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
        finished = False
        self.enemy_map.append(self.map_start)
        while not finished:
            finished = True
            for direct in directions:
                if direct[0] == int(-self.map_direction[0]) and direct[1] == int(-self.map_direction[1]):
                    continue
                elif 0 <= self.map_start[0]+direct[0] < len(self.map) and\
                        0 <= self.map_start[1]+direct[1] < len(self.map[0]):
                    if self.map[self.map_start[0]+direct[0]][self.map_start[1]+direct[1]] == 1:
                        self.map_direction = direct
                        self.map_start = (self.map_start[0]+direct[0], self.map_start[1]+direct[1])
                        self.enemy_map.append(self.map_start)
                        finished = False
                        break
                    else:
                        pass

    def draw_level(self, window):
        for row_count, row in enumerate(self.map):
            for tile_count, tile in enumerate(row):
                draw_tile(window, (tile_count*TILE_SIZE, row_count*TILE_SIZE), self.map_colors[tile])

    def draw_ui(self, window):
        window.fill(pg.color.Color('aquamarine'), pg.rect.Rect(960, 0, 256, 960))
        for button in self.menu_buttons:
            blit_text_object(window, button[1])

    def run(self):
        if self.player["lives"] <= 0:
            pass
        if self.current_round.started:
            self.current_round.check_state(self.player)
        if self.current_round.ended:
            self.round_number += 1
            self.current_round = NewRound(self.round_number, self.enemy_map)

    def check_event(self, event):
        if not self.current_round.started:
            if event.type == pg.MOUSEBUTTONDOWN:
                self.current_round.started = True

    def draw(self, window):
        self.draw_level(window)
        self.draw_ui(window)
        if self.current_round.started:
            for enemy in self.current_round.enemies:
                enemy.draw(window)


class Controller:
    def __init__(self):
        self.frame_rate = 30
        self.timer = 0
        self.screen_size = SCREEN_SIZE
        self.clock = pg.time.Clock()
        self.window = pg.display.get_surface()
        self.running = True
        self.scenes = {"main_menu": MainMenu(), "pause_menu": PauseMenu(), "options": Options(), "map": Game()}
        self.current_scene = self.scenes['main_menu']

    def sort_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
            else:
                self.current_scene.check_event(event)

    def check_for_switch(self):
        if self.current_scene.command is not None:
            self.current_scene = self.scenes[self.current_scene.command]
            self.current_scene.reset()

    def main_loop(self):
        while self.running:
            self.clock.tick(self.frame_rate)
            self.sort_events()
            self.check_for_switch()
            self.current_scene.run()
            self.current_scene.draw(self.window)
            pg.display.update()


if __name__ == "__main__":
    os.environ["SDL_VIDEO_CENTERED"] = "True"
    pg.init()
    FONTS = {"BIG": pg.font.SysFont("helvetica", 100, True),
             "MEDIUM": pg.font.SysFont("helvetica", 50, True),
             "SMALL": pg.font.SysFont("helvetica", 30, True)}
    pg.display.set_caption(GAME_CAPTION)
    display_info = pg.display.Info()
    SCREEN_SIZE = (display_info.current_w, display_info.current_h)
    pg.display.set_mode((960+256, 960))
    Controller().main_loop()
