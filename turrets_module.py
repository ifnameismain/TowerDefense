import pygame as pg
import math
from main import TILE_SIZE


class Turret:
    def __init__(self):
        self.image_to_draw = None
        self.rect = None
        self.x = 0
        self.y = 0
        self.image = None

    def change_angle(self, x, y):
        x = x
        y = y
        x_diff = self.x + TILE_SIZE//2 - x
        y_diff = self.y + TILE_SIZE//2 - y
        if y_diff != 0:
            if 0 <= x_diff and 0 < y_diff:
                angle = math.atan(abs(x_diff/y_diff))
            elif y_diff < 0 <= x_diff:
                angle = math.pi - math.atan(abs(x_diff/y_diff))
            elif x_diff <= 0 < y_diff:
                angle = (2*math.pi) - math.atan(abs(x_diff/y_diff))
            else:
                angle = math.pi + math.atan(abs(x_diff/y_diff))
        else:
            if x_diff < 0:
                angle = 3*math.pi/2
            else:
                angle = math.pi/2
        self.image_to_draw = pg.transform.rotate(self.image, 180*angle/math.pi)
        self.rect = self.image_to_draw.get_rect(center=self.image.get_rect(topleft=(self.x, self.y)).center)

    def draw(self, window):
        window.blit(self.image_to_draw, self.rect)


class BasicTurret(Turret):
    def __init__(self):
        Turret.__init__(self)
        self.damage = 10
        self.firerate = 30
        self.range = 100
        self.x = 300
        self.y = 260
        self.rect = pg.rect.Rect(self.x, self.y, 64, 64)
        self.image = pg.image.load("static/turrets/awful_turret.png").copy().convert_alpha()
        self.image = pg.transform.scale(self.image, (64, 64))
        self.image_to_draw = self.image.copy()
