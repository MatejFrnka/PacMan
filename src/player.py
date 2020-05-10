from pyglet.window import key
from src.assetsmanager import Direction
import src.assetsmanager as assets
import src.globalsettings as settings
import pyglet
import src.movement as movement
from abc import ABC
import pyglet.image
import math
import numpy as np


class Player(ABC):
    def __init__(self, bit_map, sp_texture, x_offset=None, y_offset=None):
        if x_offset is None:
            x_offset = 0
        if y_offset is None:
            y_offset = 0

        self.bit_map = bit_map
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.sprite = pyglet.sprite.Sprite(sp_texture,
                                           x=settings.BLOCK_SIZE + self.x_offset,
                                           y=settings.BLOCK_SIZE + self.y_offset)
        self.sprite.scale = settings.BLOCK_SIZE / self.sprite.height
        self.direction = movement.getDirection(Direction.STOP)

    def update(self, dt):
        self.direction.move(self.sprite, self._availableDir(), dt)

    def keypress(self, symbol):
        pass

    def draw(self):
        self.sprite.draw()

    def _availableDir(self):
        y, x = self.getPosInMap(False)
        ey, ex = self.getPosInMap(True)

        return self.direction.availableDir(y, x, ey, ex, self.bit_map)

    # returns position (y, x), if exact is True it returns float else integer
    def getPosInMap(self, exact=None):
        if exact is None:
            exact = False

        res = self._translateCordToScreen((self.sprite.y - self.y_offset) / settings.BLOCK_SIZE,
                                          (self.sprite.x - self.x_offset) / settings.BLOCK_SIZE)
        if not exact:
            res = (round(res[0]), round(res[1]))
        return res

    # takes y, x index of bit_map and returns its position on screen
    def _translateCordToScreen(self, y, x):
        return self.bit_map.shape[0] - y - 1, x


class Human(Player):
    def __init__(self, bit_map, x_offset=None, y_offset=None, keyTranslate=None):
        super(Human, self).__init__(bit_map, x_offset=x_offset, y_offset=y_offset, sp_texture=assets.pacman)
        if keyTranslate is not None:
            self.keyDirTranslate = keyTranslate
        self.nextDirection = None
        self.turnAt = None

    keyDirTranslate = {
        key.UP: Direction.UP,
        key.DOWN: Direction.DOWN,
        key.LEFT: Direction.LEFT,
        key.RIGHT: Direction.RIGHT,
    }

    def keypress(self, symbol):
        if symbol not in self.keyDirTranslate:
            return
        a = self._availableDir()
        self.nextDirection = self.keyDirTranslate[symbol]

    def update(self, dt):
        directions = self._availableDir()
        if self.nextDirection in directions:
            self.direction = movement.getDirection(self.nextDirection)
            # self.sprite.rotation = self.direction.angle
            self.nextDirection = None
        Player.update(self, dt)


class Ghost(Player):
    x_target = 20
    y_target = 0

    def __init__(self, bit_map, sp_texture, pacman, behaviour, x_offset, y_offset):
        super().__init__(bit_map, sp_texture, x_offset=x_offset, y_offset=y_offset)
        self.pacman = pacman
        self.targetBehaviour = behaviour

    def _calcDistFrom(self, y, x):
        y_dif = y - self.y_target
        x_dif = x - self.x_target
        return math.sqrt(math.pow(y_dif, 2) + math.pow(x_dif, 2))

    def _getClosestDirection(self, directions):
        closest = None
        for d in directions:
            dist = self._calcDistFrom(*np.array(self.getPosInMap()) + np.array(movement.getDirection(d).direction))
            if closest is None or closest[0] > dist:
                closest = (dist, d)

        return closest[1]

    def _makeDecision(self):
        directions = self._availableDir()
        # ghosts are not allowed to turn around

        if self.direction.opposite in directions:
            directions.remove(self.direction.opposite)
        direction = self._getClosestDirection(directions)
        self.direction = movement.getDirection(direction)

    def update(self, dt):
        self._makeDecision()
        Player.update(self, dt)
        self.y_target, self.x_target = self.targetBehaviour.updateTarget(self.pacman)
