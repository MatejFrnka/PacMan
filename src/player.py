from pyglet.window import key
from src.assetsmanager import Direction
import src.assetsmanager as assets
import src.globalsettings as settings
import pyglet
from abc import ABC


class Player(ABC):
    def __init__(self, bit_map, sp_texture):
        self.bit_map = bit_map
        self.sprite = pyglet.sprite.Sprite(sp_texture, x=settings.BLOCK_SIZE, y=settings.BLOCK_SIZE)
        self.sprite.scale = settings.BLOCK_SIZE / self.sprite.height
        self.direction = Direction.STOP
        self.nextDirection = None

    def update(self, dt):
        pass

    def keypress(self, symbol):
        pass

    def draw(self):
        self.sprite.draw()


class Human(Player):
    def __init__(self, bit_map, keyTranslate=None):
        super(Human, self).__init__(bit_map, assets.pacman)
        if keyTranslate is not None:
            self.keyDirTranslate = keyTranslate

    keyDirTranslate = {
        key.UP: Direction.UP,
        key.DOWN: Direction.DOWN,
        key.LEFT: Direction.LEFT,
        key.RIGHT: Direction.RIGHT,
    }

    def keypress(self, symbol):
        if symbol not in self.keyDirTranslate:
            return
        self.nextDirection = self.keyDirTranslate[symbol]

    # returns position (y, x), if exact is True it returns float else integer
    def getPosInMap(self, exact=None):
        if exact is None:
            exact = False
        if exact:
            return tuple((self.bit_map.shape[0] - self.sprite.y / settings.BLOCK_SIZE - 1,
                          self.sprite.x / settings.BLOCK_SIZE))
        return tuple((self.bit_map.shape[0] - round(self.sprite.y / settings.BLOCK_SIZE) - 1,
                      round(self.sprite.x / settings.BLOCK_SIZE)))

    def availableDir(self):
        y, x = self.getPosInMap(False)
        ey, ex = self.getPosInMap(True)
        result = []
        epsilon = 0.1
        ct_y = 0 if abs(y - ey) > epsilon else 1
        ct_x = 0 if abs(x - ex) > epsilon else 1
        if 0 < y:
            if self.bit_map[y - 1 * ct_y][x] != 1:
                result.append(Direction.UP)
        if y < self.bit_map.shape[0] - 1:
            if self.bit_map[y + 1 * ct_y][x] != 1:
                result.append(Direction.DOWN)
        if 0 < x:
            if self.bit_map[y][x - 1 * ct_x] != 1:
                result.append(Direction.LEFT)
        if x < self.bit_map.shape[1] - 1:
            if self.bit_map[y][x + 1 * ct_x] != 1:
                result.append(Direction.RIGHT)
        return result

    def update(self, dt):
        directions = self.availableDir()
        if self.nextDirection in directions:
            self.direction = self.nextDirection
            self.nextDirection = None
        epsilon = 0.1
        if self.direction == Direction.LEFT or self.direction == Direction.RIGHT:
            dif = (round(self.sprite.y / settings.BLOCK_SIZE) * settings.BLOCK_SIZE) - self.sprite.y
            if dif > epsilon:
                self.sprite.y += settings.MOVEMENT_SPEED * dt * abs(dif / 10)
            elif dif < epsilon:
                self.sprite.y -= settings.MOVEMENT_SPEED * dt * abs(dif / 10)
            print(dif)
        elif self.direction == Direction.UP or self.direction == Direction.DOWN:
            dif = (round(self.sprite.x / settings.BLOCK_SIZE) * settings.BLOCK_SIZE) - self.sprite.x
            if dif > epsilon:
                self.sprite.x += settings.MOVEMENT_SPEED * dt * abs(dif / 10)
            elif dif < epsilon:
                self.sprite.x -= settings.MOVEMENT_SPEED * dt * abs(dif / 10)
            print(dif)

        if self.direction == Direction.DOWN and Direction.DOWN in directions:
            self.sprite.y += settings.MOVEMENT_SPEED * dt * -1
        elif self.direction == Direction.UP and Direction.UP in directions:
            self.sprite.y += settings.MOVEMENT_SPEED * dt
        if self.direction == Direction.LEFT and Direction.LEFT in directions:
            self.sprite.x += settings.MOVEMENT_SPEED * dt * -1
        if self.direction == Direction.RIGHT and Direction.RIGHT in directions:
            self.sprite.x += settings.MOVEMENT_SPEED * dt
