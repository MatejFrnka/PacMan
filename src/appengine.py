import pyglet
import pyglet.gl
from pyglet.window import key
import src.assetsmanager as assets
import src.globalsettings as settings


class Player:
    def __init__(self):
        self.image = assets.pacman

        self.sprite = pyglet.sprite.Sprite(self.image, x=50, y=50)
        self.direction = 1

    def update(self, dt):
        self.sprite.x += settings.MOVEMENT_SPEED * dt


class AppEngine(pyglet.window.Window):
    def __init__(self):
        super().__init__(1280, 700, "PAC-MAN", resizable=True)
        self.set_minimum_size(800, 600)
        self.player = Player()
        self.event_loop = pyglet.app.EventLoop()
        pyglet.clock.schedule_interval(self.update, 1 / 120.0)

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.close()

    def update(self, dt):
        self.player.update(dt)

    def on_draw(self):
        self.clear()
        self.player.sprite.draw()
