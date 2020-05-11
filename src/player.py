from pyglet.window import key
from src.assetsmanager import Direction
import src.assetsmanager as assets
import src.globalsettings as settings
import pyglet
import src.movement as movement
from abc import ABC
import pyglet.image
import numpy as np
from threading import Timer
import random


def distance(coordinatesA, coordinatesB):
    return pow(float(np.sum(np.power(coordinatesA - coordinatesB, 2))), 0.5)


class Player(ABC):
    normal_speed = 1
    dead = False
    previous_dead = dead

    def __init__(self, bit_map, sp_texture, start_x, start_y, x_offset=None, y_offset=None):
        if x_offset is None:
            x_offset = 0
        if y_offset is None:
            y_offset = 0

        self.bit_map = bit_map
        self.x_offset = x_offset
        self.y_offset = y_offset
        self.sprite = pyglet.sprite.Sprite(sp_texture,
                                           x=settings.BLOCK_SIZE * start_x + self.x_offset,
                                           y=settings.BLOCK_SIZE * start_y + self.y_offset)
        self.sprite.scale = settings.BLOCK_SIZE / self.sprite.height
        self.direction = movement.getDirection(Direction.STOP)

    def collides(self, playerB):
        pA = np.array(self.getPosInMap(True))
        pB = np.array(playerB.getPosInMap(True))
        dist = distance(np.array(self.getPosInMap(True)), np.array(playerB.getPosInMap(True)))
        return dist < 0.7

    def die(self):
        self.dead = True

    # coordinates are np.array in format y, x
    def update(self, dt):
        self.direction.move(self.sprite, self._availableDir(), dt * self.normal_speed)

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
    def __init__(self, bit_map, x, y, x_offset=None, y_offset=None, keyTranslate=None):
        super(Human, self).__init__(bit_map, x_offset=x_offset, y_offset=y_offset, sp_texture=assets.getPacman(Direction.UP),
                                    start_x=x, start_y=y)
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
            self.sprite.image = assets.getPacman(self.direction.current)
            self.nextDirection = None
        Player.update(self, dt)


class Ghost(Player):
    x_target = 0
    y_target = 0
    prev_direction = Direction.STOP
    scared = False
    warn = False
    locked = True
    scared_speed = 0.6
    dead_speed = 1.2

    def __init__(self, bit_map, sp_texture, pacman, behaviour, x_offset, y_offset):
        self.texture = sp_texture
        super().__init__(bit_map, assets.getGhost(Direction.UP, self.texture), x_offset=x_offset, y_offset=y_offset,
                         start_x=bit_map.shape[1] // 2, start_y=bit_map.shape[0] // 2)
        self.pacman = pacman
        self.targetBehaviour = behaviour

    def _getClosestDirection(self, directions):
        closest = None
        for d in directions:
            dist = distance(np.array(self.getPosInMap()) + np.array(movement.getDirection(d).direction),
                            np.array([self.y_target, self.x_target]))
            if closest is None or closest[0] > dist:
                closest = (dist, d)
        if closest is None:
            return Direction.STOP
        return closest[1]

    def _makeDecision(self):
        directions = self._availableDir()
        if len(directions) == 1:
            self.direction = movement.getDirection(directions[0])
        # players are not allowed to turn around
        if self.direction.opposite in directions:
            directions.remove(self.direction.opposite)
        # if locked remove direction up
        if self.locked and Direction.UP in directions:
            directions.remove(Direction.UP)
        # if not locked but in spawn and can go up, go up
        if not self.locked \
                and self.getPosInMap() == (self.bit_map.shape[0] // 2, self.bit_map.shape[1] // 2) \
                and Direction.UP in directions:
            self.direction = movement.getDirection(Direction.UP)
        # if scared but not dead move randomly
        elif self.scared and not self.dead:
            self.direction = movement.getDirection(random.choice(directions))
        # else go to square closest to target
        else:
            direction = self._getClosestDirection(directions)
            self.direction = movement.getDirection(direction)

    def update(self, dt):
        if (self.prev_direction != self.direction.current and not self.scared and not self.warn) \
                or (not self.scared and self.warn) \
                or self.dead:
            texture = assets.ghost_eyes if self.dead else self.texture
            self.sprite.image = assets.getGhost(self.direction.current, texture)
            self.prev_direction = self.direction.current
            self.warn = False
        if self.warn and self.scared:
            self.warn = False
            self.sprite.image = assets.getScared(True)
        self._makeDecision()
        multiplier = 1
        if self.dead:
            multiplier = self.dead_speed
        elif self.scared:
            multiplier = self.scared_speed
        Player.update(self, dt * multiplier)
        if self.dead:

            self.y_target = self.bit_map.shape[0] // 2
            self.x_target = self.bit_map.shape[1] // 2
            tmp = self.getPosInMap()
            if self.getPosInMap() == (self.y_target, self.x_target):
                self.respawn()
        if not self.dead:
            self.y_target, self.x_target = self.targetBehaviour.updateTarget()

    def keypress(self, symbol):
        pass

    def draw(self):
        Player.draw(self)

    def respawn(self):
        self.dead = False
        self.scared = False
        self.direction = movement.getDirection(self.direction.opposite)
        self.sprite.image = assets.getGhost(self.direction.current, self.texture)

    # time - time to be scared. min time is 1.5 seconds
    def scare(self, time):
        if time < 1.5:
            time = 1.5

        def warn():
            self.warn = True
            Timer(1.5, unscare).start()

        def unscare():
            self.scared = False
            self.warn = True
            self.current_speed = self.normal_speed

        self.scared = True
        self.sprite.image = assets.getScared(False)
        self.direction = movement.getDirection(self.direction.opposite)
        self.current_speed = self.scared_speed

        t = Timer(time - 1.5, warn)
        t.start()
