from abc import ABC
from src.assetsmanager import Direction
import src.globalsettings as settings
import numpy as np


class AbstractDirection(ABC):
    vertical = None
    epsilon = 0.1
    dif_multiplier = 0.2
    angle = 0

    def calc_dif(self, variable):
        return (round(variable / settings.BLOCK_SIZE) * settings.BLOCK_SIZE) - variable

    def _isVertical(self, direction):
        return direction in [Direction.UP, Direction.DOWN]

    def move(self, sprite, direction, dt):
        pass

    def availableDir(self, y, x, ey, ex, bit_map):
        ct_y = 0 if abs(y - ey) > self.epsilon else 1
        ct_x = 0 if abs(x - ex) > self.epsilon else 1
        result = []
        if bit_map[y - 1 * ct_y][x] != 1:
            result.append(Direction.UP)
        if bit_map[y + 1 * ct_y][x] != 1:
            result.append(Direction.DOWN)
        if bit_map[y][x - 1 * ct_x] != 1:
            result.append(Direction.LEFT)
        if bit_map[y][x + 1 * ct_x] != 1:
            result.append(Direction.RIGHT)
        return result


class VerticalDirection(AbstractDirection):
    vertical = True

    def move(self, sprite, direction, dt):
        dif = self.calc_dif(sprite.x)
        if dif > self.epsilon:
            sprite.x += settings.MOVEMENT_SPEED * dt * abs(dif * self.dif_multiplier)
        elif dif < self.epsilon:
            sprite.x -= settings.MOVEMENT_SPEED * dt * abs(dif * self.dif_multiplier)


class HorizontalDirection(AbstractDirection):
    vertical = False

    def move(self, sprite, direction, dt):
        dif = self.calc_dif(sprite.y)
        if dif > self.epsilon:
            sprite.y += settings.MOVEMENT_SPEED * dt * abs(dif * self.dif_multiplier)
        elif dif < self.epsilon:
            sprite.y -= settings.MOVEMENT_SPEED * dt * abs(dif * self.dif_multiplier)


class Stop(AbstractDirection):
    def move(self, sprite, direction, distance):
        return


class Up(VerticalDirection):
    angle = 90

    def move(self, sprite, directions, dt):
        if Direction.UP in directions:
            sprite.y += settings.MOVEMENT_SPEED * dt
            VerticalDirection.move(self, sprite, directions, dt)

    def availableDir(self, y, x, ey, ex, bit_map):
        result = AbstractDirection.availableDir(self, y, x, ey, ex, bit_map)
        if ey < y:
            result = [val for val in result if self._isVertical(val)]
        return result


class Down(VerticalDirection):
    angle = 270

    def move(self, sprite, directions, dt):
        if Direction.DOWN in directions:
            sprite.y -= settings.MOVEMENT_SPEED * dt
            VerticalDirection.move(self, sprite, directions, dt)

    def availableDir(self, y, x, ey, ex, bit_map):
        result = AbstractDirection.availableDir(self, y, x, ey, ex, bit_map)
        if ey > y:
            result = [val for val in result if self._isVertical(val)]
        return result


class Left(HorizontalDirection):
    angle = 0

    def move(self, sprite, directions, dt):
        if Direction.LEFT in directions:
            sprite.x -= settings.MOVEMENT_SPEED * dt
            HorizontalDirection.move(self, sprite, directions, dt)

    def availableDir(self, y, x, ey, ex, bit_map):
        result = AbstractDirection.availableDir(self, y, x, ey, ex, bit_map)
        if ex < x:
            result = [val for val in result if not self._isVertical(val)]
        return result


class Right(HorizontalDirection):
    angle = 180

    def move(self, sprite, directions, dt):
        if Direction.RIGHT in directions:
            sprite.x += settings.MOVEMENT_SPEED * dt
            HorizontalDirection.move(self, sprite, directions, dt)

    def availableDir(self, y, x, ey, ex, bit_map):
        result = AbstractDirection.availableDir(self, y, x, ey, ex, bit_map)
        if ex > x:
            result = [val for val in result if not self._isVertical(val)]
        return result


def getDirection(direction):
    if direction == Direction.UP:
        return Up()
    if direction == Direction.STOP:
        return Stop()
    if direction == Direction.DOWN:
        return Down()
    if direction == Direction.LEFT:
        return Left()
    if direction == Direction.RIGHT:
        return Right()
