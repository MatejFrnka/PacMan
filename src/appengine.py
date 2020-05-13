import pyglet
import pyglet.gl
from pyglet.window import key
import src.assetsmanager as assets
import src.globalsettings as settings
from src.map import Map


class AppEngine(pyglet.window.Window):
    def __init__(self):
        bit_map = assets.generateMap()
        super().__init__(bit_map.shape[1] * settings.BLOCK_SIZE, bit_map.shape[0] * settings.BLOCK_SIZE + settings.BLOCK_SIZE * 3, "PAC-MAN", resizable=False)
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