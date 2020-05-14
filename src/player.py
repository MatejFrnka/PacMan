import pyglet
from src.assetsmanager import EnumDirection
import src.assetsmanager as assets
import src.globalsettings as settings
import src.movement as movement
from abc import ABC
import numpy as np
from threading import Timer
import random


# calculates distance between two points (y, x)
def distance(coordinatesA, coordinatesB):
    return pow(float(np.sum(np.power(coordinatesA - coordinatesB, 2))), 0.5)


"""
Abstract class, implements basic player movement
"""


class Player(ABC):
    """
    :param bit_map 2d np.array of map. See more info in assetsmanager.py
    :param sp_texture Texture to use for player
    :param start_x start x position
    :param start_y start y position
    :param x_offset X offset of map
    :param y_offset Y offset of map
    """

    def __init__(self, bit_map, sp_texture, start_x, start_y, x_offset=None, y_offset=None):

        self.normal_speed = 1
        self.dead = False
        self.previous_dead = self.dead
        if x_offset is None:
            x_offset = 0
        if y_offset is None:
            y_offset = 0
        self.bit_map = bit_map
        self.x_offset = x_offset
        self.y_offset = y_offset
        y, x = self._translate_cord_to_screen(start_y, start_x)
        self.sprite = pyglet.sprite.Sprite(sp_texture,
                                           x=settings.BLOCK_SIZE * x + self.x_offset,
                                           y=settings.BLOCK_SIZE * y + self.y_offset)
        self.sprite.scale = settings.BLOCK_SIZE / self.sprite.height
        self.direction = movement.get_direction(EnumDirection.STOP)

    """
    Check collision with another player
    """

    def collides(self, playerB):
        pA = np.array(self.get_pos_in_map(True))
        pB = np.array(playerB.get_pos_in_map(True))
        dist = distance(np.array(self.get_pos_in_map(True)), np.array(playerB.get_pos_in_map(True)))
        return dist < 0.7

    """
    Kills player
    """

    def die(self):
        self.dead = True

    def update(self, dt):
        self.direction.move(self.sprite, self._available_dir(), dt * self.normal_speed)

    def keypress(self, symbol):
        pass

    def draw(self):
        self.sprite.draw()

    # returns EnumDirection
    def _available_dir(self):
        y, x = self.get_pos_in_map(False)
        ey, ex = self.get_pos_in_map(True)
        return self.direction.available_dir(y, x, ey, ex, self.bit_map)

    # returns position (y, x), if exact is True it returns float else integer
    def get_pos_in_map(self, exact=None):
        if exact is None:
            exact = False

        res = self._translate_cord_to_screen((self.sprite.y - self.y_offset) / settings.BLOCK_SIZE,
                                             (self.sprite.x - self.x_offset) / settings.BLOCK_SIZE)
        if not exact:
            res = (round(res[0]), round(res[1]))
        return res

    # takes y, x index of bit_map and returns its position on screen
    def _translate_cord_to_screen(self, y, x):
        return self.bit_map.shape[0] - y - 1, x


"""
Human controlled player
"""


class Human(Player):
    def __init__(self, bit_map, x, y, x_offset=None, y_offset=None, key_map=None):
        super(Human, self).__init__(bit_map, x_offset=x_offset, y_offset=y_offset, sp_texture=assets.get_pacman(EnumDirection.UP),
                                    start_x=x, start_y=y)

        self.enum_next_direction = EnumDirection.STOP
        if key_map is None:
            self.keyDirTranslate = {
                pyglet.window.key.UP: EnumDirection.UP,
                pyglet.window.key.DOWN: EnumDirection.DOWN,
                pyglet.window.key.LEFT: EnumDirection.LEFT,
                pyglet.window.key.RIGHT: EnumDirection.RIGHT,
            }
        else:
            self.keyDirTranslate = key_map

    def keypress(self, symbol):
        if symbol not in self.keyDirTranslate:
            return
        a = self._available_dir()
        self.enum_next_direction = self.keyDirTranslate[symbol]

    def update(self, dt):
        directions = self._available_dir()
        if self.enum_next_direction in directions:
            self.direction = movement.get_direction(self.enum_next_direction)
            self.sprite.image = assets.get_pacman(self.direction.current)
            self.enum_next_direction = None
        Player.update(self, dt)


"""
Player controlled by GhostBehaviour class
"""


class Ghost(Player):

    def __init__(self, bit_map, sp_texture, pacman, behaviour, x_offset=None, y_offset=None):
        self.x_target = 0
        self.y_target = 0
        self.prev_direction = EnumDirection.STOP
        self.scared = False
        self.warn = False
        self.locked = True
        self.scared_speed = 0.6
        self.dead_speed = 1.2

        self.texture = sp_texture
        super().__init__(bit_map, assets.get_ghost(EnumDirection.UP, self.texture), x_offset=x_offset, y_offset=y_offset,
                         start_x=bit_map.shape[1] // 2, start_y=bit_map.shape[0] // 2)
        self.pacman = pacman
        self.targetBehaviour = behaviour
        self.scare_timer = None

    # returns EnumDirection
    def _get_closest_direction(self, enum_directions):
        closest = None
        for d in enum_directions:
            dist = distance(np.array(self.get_pos_in_map()) + np.array(movement.get_direction(d).direction),
                            np.array([self.y_target, self.x_target]))
            if closest is None or closest[0] > dist:
                closest = (dist, d)
        if closest is None:
            return EnumDirection.STOP
        return closest[1]

    def _make_decision(self):
        enum_directions = self._available_dir()
        if len(enum_directions) == 1:
            self.direction = movement.get_direction(enum_directions[0])
        # players are not allowed to turn around
        if self.direction.opposite in enum_directions:
            enum_directions.remove(self.direction.opposite)
        # if locked remove direction up
        if self.locked and EnumDirection.UP in enum_directions:
            enum_directions.remove(EnumDirection.UP)
        # if not locked but in spawn and can go up, go up
        if not self.locked \
                and self.get_pos_in_map() == (self.bit_map.shape[0] // 2, self.bit_map.shape[1] // 2) \
                and EnumDirection.UP in enum_directions:
            self.direction = movement.get_direction(EnumDirection.UP)
        # if scared but not dead move randomly
        elif self.scared and not self.dead:
            self.direction = movement.get_direction(random.choice(enum_directions))
        # else go to square closest to target
        else:
            self.direction = movement.get_direction(self._get_closest_direction(enum_directions))

    def update(self, dt):
        if (self.prev_direction != self.direction.current and not self.scared and not self.warn) \
                or (not self.scared and self.warn) \
                or self.dead:
            texture = assets.GHOST_EYES if self.dead else self.texture
            self.sprite.image = assets.get_ghost(self.direction.current, texture)
            self.prev_direction = self.direction.current
            self.warn = False
        if self.warn and self.scared:
            self.warn = False
            self.sprite.image = assets.get_scared(True)
        self._make_decision()
        multiplier = 1
        if self.dead:
            multiplier = self.dead_speed
        elif self.scared:
            multiplier = self.scared_speed
        Player.update(self, dt * multiplier)
        if self.dead:

            self.y_target = self.bit_map.shape[0] // 2
            self.x_target = self.bit_map.shape[1] // 2
            tmp = self.get_pos_in_map()
            if self.get_pos_in_map() == (self.y_target, self.x_target):
                self.respawn()
        if not self.dead:
            self.y_target, self.x_target = self.targetBehaviour.update_target()

    def keypress(self, symbol):
        pass

    def draw(self):
        Player.draw(self)

    def respawn(self):
        self.dead = False
        self.scared = False
        self.direction = movement.get_direction(self.direction.opposite)
        self.sprite.image = assets.get_ghost(self.direction.current, self.texture)

    # time - time to be scared. min time is 1.5 seconds
    def scare(self, time):
        if time < 1.5:
            time = 1.5

        def warn():
            self.warn = True
            self.scare_timer = Timer(1.5, unscare)
            self.scare_timer.start()

        def unscare():
            self.scared = False
            self.warn = True

        self.scared = True
        self.sprite.image = assets.get_scared(False)
        self.direction = movement.get_direction(self.direction.opposite)
        if self.scare_timer is not None:
            self.scare_timer.cancel()
        self.scare_timer = Timer(time - 1.5, warn)
        self.scare_timer.start()
