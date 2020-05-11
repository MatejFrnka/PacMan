import pyglet
import pyglet.gl
from pyglet.window import key
import src.assetsmanager as assets
import src.globalsettings as settings
import src.player as pl
from src.map import Map


class AppEngine(pyglet.window.Window):
    def __init__(self):
        super().__init__(19 * settings.BLOCK_SIZE, 19 * settings.BLOCK_SIZE + settings.BLOCK_SIZE * 3, "PAC-MAN", resizable=False)
        bit_map = assets.generateMap()
        self.map = Map(bit_map)
        self.event_loop = pyglet.app.EventLoop()
        pyglet.clock.schedule_interval(self.update, 1 / 120.0)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.close()
        self.map.keypress(symbol)

    def update(self, dt):
        self.map.update(dt)

    def on_draw(self):
        self.clear()
        self.map.draw()