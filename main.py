import pygame as pg
import os
from pg_funcs import *
import shelve
import random
import json


# Globals
GAME_CAPTION = "Tower Defense"
COLORS = {'black': pg.color.Color('black'), 'white': pg.color.Color('white')}

def get_mouse():
    return pg.mouse.get_pos()


class Player:
    def __init__(self, money=500):
        self.money = money
        self.highscore = 0
        self.load_player()

    def load_player(self):
        d = shelve.open('player')
        self.highscore = d['highscore']
        d.close()

    def save_player(self):
        d = shelve.open('player')
        d['highscore'] = self.highscore
        d.close()


class GenericScene:
    def __init__(self):
        self.command = None

    def draw(self, window):
        pass

    def reset(self):
        self.command = None


class MainMenu(GenericScene):
    def __init__(self):
        GenericScene.__init__(self)
        self.menu_buttons = [
            create_button((150, 150), (300, 100), text="Play", font=FONTS['SMALL']),
            create_button((150, 400), (300, 100), text="Options", font=FONTS['SMALL']),
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
        window.fill(COLORS['black'])
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
        pass


class Game(GenericScene):
    def __init__(self):
        GenericScene.__init__(self)
        self.player = Player()
        self.map = [[0] * (pg.display.Info().current_w // 64)] * (pg.display.Info().current_w // 64)
        self.choose_level()


    def choose_level(self):
        """Generate tile map here (integer representation of enemy path + obstacles)"""
        with open('static/levels.json', 'r') as f:
            self.map = json.load(f)['name']




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
            self.current_scene.draw(self.window)
            pg.display.update()


if __name__ == "__main__":
    os.environ["SDL_VIDEO_CENTERED"] = "True"
    pg.init()
    FONTS = {"BIG": pg.font.SysFont("helvetica", 100, True),
             "SMALL": pg.font.SysFont("helvetica", 50, True)}
    pg.display.set_caption(GAME_CAPTION)
    display_info = pg.display.Info()
    SCREEN_SIZE = (display_info.current_w, display_info.current_h)
    pg.display.set_mode((960, 960))
    Controller().main_loop()
