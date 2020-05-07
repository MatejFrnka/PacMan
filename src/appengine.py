import pyglet
import pyglet.gl
from pyglet.window import key
import src.assetsmanager as assets
import src.globalsettings as settings
import numpy as np


class Map:
    def __init__(self, bit_map):
        self.batch = pyglet.graphics.Batch()
        self.map = self.createMap(bit_map)

    def draw(self):
        self.batch.draw()

    def createMap(self, bit_map):
        res = []
        for y in range(bit_map.shape[0]):
            for x in range(bit_map.shape[1]):

                if bit_map[y][x] != 0:
                    sprite = pyglet.sprite.Sprite(assets.wall, x=x * settings.BLOCK_SIZE, y=y * settings.BLOCK_SIZE,
                                                  batch=self.batch)
                    sprite.scale = settings.BLOCK_SIZE / sprite.height
                    res.append(sprite)
        return res


class Player:
    def __init__(self):
        self.sprite = pyglet.sprite.Sprite(assets.pacman, x=settings.BLOCK_SIZE, y=settings.BLOCK_SIZE)
        self.sprite.scale = settings.BLOCK_SIZE / self.sprite.height
        self._direction_x = 0
        self._direction_y = 0
        self.nextKey = None

    def keypress(self, symbol):
        if symbol == key.UP and symbol in self.availableDir():
            self._direction_y = 1
            self._direction_x = 0
        if symbol == key.DOWN and symbol in self.availableDir():
            self._direction_y = -1
            self._direction_x = 0
        if symbol == key.RIGHT and symbol in self.availableDir():
            self._direction_y = 0
            self._direction_x = 1
        if symbol == key.LEFT and symbol in self.availableDir():
            self._direction_y = 0
            self._direction_x = -1

    def availableDir(self):
        return [key.UP, key.DOWN, key.LEFT, key.RIGHT]

    def update(self, dt):
        self.sprite.x += settings.MOVEMENT_SPEED * dt * self._direction_x
        self.sprite.y += settings.MOVEMENT_SPEED * dt * self._direction_y


class AppEngine(pyglet.window.Window):
    def __init__(self):
        super().__init__(1280, 700, "PAC-MAN", resizable=True)
        bit_map = assets.generateMap()
        self.map = Map(bit_map)
        
        self.set_minimum_size(800, 600)

        self.player = Player()
        self.event_loop = pyglet.app.EventLoop()
        pyglet.clock.schedule_interval(self.update, 1 / 120.0)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.close()
        self.player.keypress(symbol)

    def update(self, dt):
        self.player.update(dt)

    def on_draw(self):
        self.clear()
        self.map.draw()
        self.player.sprite.draw()
