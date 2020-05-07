from pyglet.window import key
from src.assetsmanager import Direction
import src.assetsmanager as assets
import src.globalsettings as settings
import pyglet
import src.movement as movement
from abc import ABC


class Player(ABC):
    def __init__(self, bit_map, sp_texture):
        self.bit_map = bit_map
        self.sprite = pyglet.sprite.Sprite(sp_texture, x=settings.BLOCK_SIZE, y=settings.BLOCK_SIZE)
        self.sprite.scale = settings.BLOCK_SIZE / self.sprite.height
        self.direction = movement.getDirection(Direction.STOP)

    def update(self, dt):
        pass

    def keypress(self, symbol):
        pass

    def draw(self):
        self.sprite.draw()

    def _availableDir(self, y=None, x=None):
        if y is None or x is None:
            y, x = self._getPosInMap(False)
        ey, ex = self._getPosInMap(True)
        result = []
        epsilon = 0.1
        ct_y = 0 if abs(y - ey) > epsilon else 1
        ct_x = 0 if abs(x - ex) > epsilon else 1
        if self.bit_map[y - 1 * ct_y][x] != 1:
            if self.direction == Direction.RIGHT and ex <= x or self.direction == Direction.LEFT and ex >= x or (
                    self.direction != Direction.LEFT and self.direction != Direction.RIGHT):
                result.append(Direction.UP)
        if self.bit_map[y + 1 * ct_y][x] != 1:
            if self.direction == Direction.RIGHT and ex <= x or self.direction == Direction.LEFT and ex >= x or (
                    self.direction != Direction.LEFT and self.direction != Direction.RIGHT):
                result.append(Direction.DOWN)
        if self.bit_map[y][x - 1 * ct_x] != 1:
            if self.direction == Direction.DOWN and ey <= y or self.direction == Direction.UP and ey >= y or (
                    self.direction != Direction.UP and self.direction != Direction.DOWN):
                result.append(Direction.LEFT)
        if self.bit_map[y][x + 1 * ct_x] != 1:
            if self.direction == Direction.DOWN and ey <= y or self.direction == Direction.UP and ey >= y or (
                    self.direction != Direction.UP and self.direction != Direction.DOWN):
                result.append(Direction.RIGHT)
        return result

    # returns position (y, x), if exact is True it returns float else integer
    def _getPosInMap(self, exact=None):
        if exact is None:
            exact = False
        if exact:
            return self._translateCordToScreen(self.sprite.y / settings.BLOCK_SIZE,
                                               self.sprite.x / settings.BLOCK_SIZE)
        return self._translateCordToScreen(round(self.sprite.y / settings.BLOCK_SIZE),
                                           round(self.sprite.x / settings.BLOCK_SIZE))

    # takes y, x index of bit_map and returns its position on screen
    def _translateCordToScreen(self, y, x):
        return self.bit_map.shape[0] - y - 1, x


class Human(Player):
    def __init__(self, bit_map, keyTranslate=None):
        super(Human, self).__init__(bit_map, assets.pacman)
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

    def _getMultiplier(self, direction):
        x = 0
        y = 0
        if direction == Direction.DOWN:
            y = -1
        if direction == Direction.UP:
            y = 1
        if direction == Direction.LEFT:
            x = -1
        if direction == Direction.RIGHT:
            x = 1
        return y, x

    def keypress(self, symbol):
        if symbol not in self.keyDirTranslate:
            return
        a = self._availableDir()
        self.nextDirection = self.keyDirTranslate[symbol]

    def update(self, dt):
        directions = self._availableDir()
        if self.nextDirection in directions:
            self.direction = movement.getDirection(self.nextDirection)
            self.nextDirection = None

        self.direction.move(self.sprite, directions, dt)
