from abc import ABC
from src.assetsmanager import EnumDirection
import src.globalsettings as settings
import numpy as np

"""
Abstract class that implements default movements
"""


class AbstractDirection(ABC):
    vertical = None
    epsilon = 0.1
    dif_multiplier = 0.2
    angle = 0
    """
    Calculates difference from center of the block to the variable position
    :param variable position to calculate distance from center of block
    """

    def calc_dif(self, variable):
        return (round(variable / settings.BLOCK_SIZE) * settings.BLOCK_SIZE) - variable

    """
    Check if EnumDirection is of type vertical
    :param enum_direction returns if given directino is vertical 
    """

    def _isVertical(self, enum_direction):
        return enum_direction in [EnumDirection.UP, EnumDirection.DOWN]

    """
    moves sprite in give direction
    :param sprite Sprite to move
    :param enum_direction Direction to move in
    :param dt move multiplier
    """

    def move(self, sprite, enum_direction, dt):
        pass

    """
    :param y Y position in bit_map
    :param x X position in bit_map
    :param ey Exact y position
    :param ex Exact x position
    :returns array of available directions
    """

    def availableDir(self, y, x, ey, ex, bit_map):
        ct_y = 0 if abs(y - ey) > self.epsilon else 1
        ct_x = 0 if abs(x - ex) > self.epsilon else 1
        result = []
        if 0 <= y < len(bit_map) and 0 <= x < len(bit_map[0]):
            if bit_map[y - 1 * ct_y][x] != 1:
                result.append(EnumDirection.UP)
            if bit_map[y + 1 * ct_y][x] != 1:
                result.append(EnumDirection.DOWN)
            if bit_map[y][x - 1 * ct_x] != 1:
                result.append(EnumDirection.LEFT)
            if bit_map[y][x + 1 * ct_x] != 1:
                result.append(EnumDirection.RIGHT)
        return result


class VerticalDirection(AbstractDirection):
    vertical = True
    """
    moves sprite in give direction
    :param sprite Sprite to move
    :param enum_direction Direction to move in
    :param dt move multiplier
    """

    def move(self, sprite, enum_direction, dt):
        dif = self.calc_dif(sprite.x)
        if dif > self.epsilon:
            sprite.x += settings.MOVEMENT_SPEED * dt * abs(dif * self.dif_multiplier)
        elif dif < self.epsilon:
            sprite.x -= settings.MOVEMENT_SPEED * dt * abs(dif * self.dif_multiplier)


class HorizontalDirection(AbstractDirection):
    vertical = False
    """
    moves sprite in give direction
    :param sprite Sprite to move
    :param enum_direction Direction to move in
    :param dt move multiplier
    """

    def move(self, sprite, enum_direction, dt):
        dif = self.calc_dif(sprite.y)
        if dif > self.epsilon:
            sprite.y += settings.MOVEMENT_SPEED * dt * abs(dif * self.dif_multiplier)
        elif dif < self.epsilon:
            sprite.y -= settings.MOVEMENT_SPEED * dt * abs(dif * self.dif_multiplier)


class Stop(AbstractDirection):
    # y, x
    direction = np.array([0, 0])
    opposite = EnumDirection.STOP
    current = EnumDirection.STOP
    """
    moves sprite in give direction
    :param sprite Sprite to move
    :param enum_direction Direction to move in
    :param dt move multiplier
    """

    def move(self, sprite, enum_direction, distance):
        return


class Up(VerticalDirection):
    # y, x
    direction = np.array([-1, 0])
    angle = 90
    opposite = EnumDirection.DOWN
    current = EnumDirection.UP
    """
    moves sprite in give direction
    :param sprite Sprite to move
    :param enum_direction Direction to move in
    :param dt move multiplier
    """

    def move(self, sprite, enum_directions, dt):
        if EnumDirection.UP in enum_directions:
            sprite.y += settings.MOVEMENT_SPEED * dt
            VerticalDirection.move(self, sprite, enum_directions, dt)

    """
    :param y Y position in bit_map
    :param x X position in bit_map
    :param ey Exact y position
    :param ex Exact x position
    :returns array of available directions
    """

    def availableDir(self, y, x, ey, ex, bit_map):
        result = AbstractDirection.availableDir(self, y, x, ey, ex, bit_map)
        if ey < y:
            result = [val for val in result if self._isVertical(val)]
        return result


class Down(VerticalDirection):
    # y, x
    direction = np.array([1, 0])
    angle = 270
    opposite = EnumDirection.UP
    current = EnumDirection.DOWN
    """
    moves sprite in give direction
    :param sprite Sprite to move
    :param enum_direction Direction to move in
    :param dt move multiplier
    """

    def move(self, sprite, enum_directions, dt):
        if EnumDirection.DOWN in enum_directions:
            sprite.y -= settings.MOVEMENT_SPEED * dt
            VerticalDirection.move(self, sprite, enum_directions, dt)

    """
    :param y Y position in bit_map
    :param x X position in bit_map
    :param ey Exact y position
    :param ex Exact x position
    :returns array of available directions
    """

    def availableDir(self, y, x, ey, ex, bit_map):
        result = AbstractDirection.availableDir(self, y, x, ey, ex, bit_map)
        if ey > y:
            result = [val for val in result if self._isVertical(val)]
        return result


class Left(HorizontalDirection):
    # y, x
    direction = np.array([0, -1])
    angle = 0
    opposite = EnumDirection.RIGHT
    current = EnumDirection.LEFT
    """
    moves sprite in give direction
    :param sprite Sprite to move
    :param enum_direction Direction to move in
    :param dt move multiplier
    """
    def move(self, sprite, enum_directions, dt):
        if EnumDirection.LEFT in enum_directions:
            sprite.x -= settings.MOVEMENT_SPEED * dt
            HorizontalDirection.move(self, sprite, enum_directions, dt)
    """
    :param y Y position in bit_map
    :param x X position in bit_map
    :param ey Exact y position
    :param ex Exact x position
    :returns array of available directions
    """
    def availableDir(self, y, x, ey, ex, bit_map):
        result = AbstractDirection.availableDir(self, y, x, ey, ex, bit_map)
        if ex < x:
            result = [val for val in result if not self._isVertical(val)]
        return result


class Right(HorizontalDirection):
    # y, x
    direction = np.array([0, 1])
    angle = 180
    opposite = EnumDirection.LEFT
    current = EnumDirection.RIGHT
    """
    moves sprite in give direction
    :param sprite Sprite to move
    :param enum_direction Direction to move in
    :param dt move multiplier
    """
    def move(self, sprite, enum_directions, dt):
        if EnumDirection.RIGHT in enum_directions:
            sprite.x += settings.MOVEMENT_SPEED * dt
            HorizontalDirection.move(self, sprite, enum_directions, dt)
    """
    :param y Y position in bit_map
    :param x X position in bit_map
    :param ey Exact y position
    :param ex Exact x position
    :returns array of available directions
    """
    def availableDir(self, y, x, ey, ex, bit_map):
        result = AbstractDirection.availableDir(self, y, x, ey, ex, bit_map)
        if ex > x:
            result = [val for val in result if not self._isVertical(val)]
        return result

"""
Direction factory, creates direction from EnumDirection
:param enum_direction EnumDirecetion of direction to get
"""
def getDirection(enum_direction):
    if enum_direction == EnumDirection.UP:
        return Up()
    if enum_direction == EnumDirection.STOP:
        return Stop()
    if enum_direction == EnumDirection.DOWN:
        return Down()
    if enum_direction == EnumDirection.LEFT:
        return Left()
    if enum_direction == EnumDirection.RIGHT:
        return Right()
