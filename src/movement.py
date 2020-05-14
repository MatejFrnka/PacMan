from abc import ABC
from src.assetsmanager import EnumDirection
import src.globalsettings as settings
import numpy as np


class AbstractDirection(ABC):
    """
    Abstract class that implements default movements
    """

    def __init__(self):
        self.vertical = None
        self.epsilon = 0.1
        self.dif_multiplier = 0.2
        self.angle = 0

    def calc_dif(self, variable):
        """
        Calculates difference from center of the block to the variable position
        :param variable position to calculate distance from center of block
        """
        return (round(variable / settings.BLOCK_SIZE) * settings.BLOCK_SIZE) - variable

    def _is_vertical(self, enum_direction):
        """
        Check if EnumDirection is of type vertical
        :param enum_direction returns if given directino is vertical
        """
        return enum_direction in [EnumDirection.UP, EnumDirection.DOWN]

    def move(self, sprite, enum_direction, dt):
        """
        moves sprite in give direction
        :param sprite Sprite to move
        :param enum_direction Direction to move in
        :param dt move multiplier
        """
        pass

    def available_dir(self, y, x, ey, ex, bit_map):
        """
        :param y Y position in bit_map
        :param x X position in bit_map
        :param ey Exact y position
        :param ex Exact x position
        :returns array of available directions
        """
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
    """
    moves sprite in give direction
    :param sprite Sprite to move
    :param enum_direction Direction to move in
    :param dt move multiplier
    """
    vertical = True

    def move(self, sprite, enum_direction, dt):
        dif = self.calc_dif(sprite.x)
        if dif > self.epsilon:
            sprite.x += settings.MOVEMENT_SPEED * dt * abs(dif * self.dif_multiplier)
        elif dif < self.epsilon:
            sprite.x -= settings.MOVEMENT_SPEED * dt * abs(dif * self.dif_multiplier)


class HorizontalDirection(AbstractDirection):
    vertical = False

    def move(self, sprite, enum_direction, dt):
        """
        moves sprite in give direction
        :param sprite Sprite to move
        :param enum_direction Direction to move in
        :param dt move multiplier
        """

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

    def move(self, sprite, enum_direction, distance):
        """
        moves sprite in give direction
        :param sprite Sprite to move
        :param enum_direction Direction to move in
        :param dt move multiplier
        """
        return


class Up(VerticalDirection):
    # y, x
    direction = np.array([-1, 0])
    angle = 90
    opposite = EnumDirection.DOWN
    current = EnumDirection.UP

    def move(self, sprite, enum_directions, dt):
        """
        moves sprite in give direction
        :param sprite Sprite to move
        :param enum_direction Direction to move in
        :param dt move multiplier
        """
        if EnumDirection.UP in enum_directions:
            sprite.y += settings.MOVEMENT_SPEED * dt
            VerticalDirection.move(self, sprite, enum_directions, dt)

    def available_dir(self, y, x, ey, ex, bit_map):
        """
        :param y Y position in bit_map
        :param x X position in bit_map
        :param ey Exact y position
        :param ex Exact x position
        :returns array of available directions
        """
        result = AbstractDirection.available_dir(self, y, x, ey, ex, bit_map)
        if ey < y:
            result = [val for val in result if self._is_vertical(val)]
        return result


class Down(VerticalDirection):
    # y, x
    direction = np.array([1, 0])
    angle = 270
    opposite = EnumDirection.UP
    current = EnumDirection.DOWN

    def move(self, sprite, enum_directions, dt):
        """
        moves sprite in give direction
        :param sprite Sprite to move
        :param enum_direction Direction to move in
        :param dt move multiplier
        """
        if EnumDirection.DOWN in enum_directions:
            sprite.y -= settings.MOVEMENT_SPEED * dt
            VerticalDirection.move(self, sprite, enum_directions, dt)

    def available_dir(self, y, x, ey, ex, bit_map):
        """
        :param y Y position in bit_map
        :param x X position in bit_map
        :param ey Exact y position
        :param ex Exact x position
        :returns array of available directions
        """

        result = AbstractDirection.available_dir(self, y, x, ey, ex, bit_map)
        if ey > y:
            result = [val for val in result if self._is_vertical(val)]
        return result


class Left(HorizontalDirection):
    # y, x
    direction = np.array([0, -1])
    angle = 0
    opposite = EnumDirection.RIGHT
    current = EnumDirection.LEFT

    def move(self, sprite, enum_directions, dt):
        """
        moves sprite in give direction
        :param sprite Sprite to move
        :param enum_direction Direction to move in
        :param dt move multiplier
        """
        if EnumDirection.LEFT in enum_directions:
            sprite.x -= settings.MOVEMENT_SPEED * dt
            HorizontalDirection.move(self, sprite, enum_directions, dt)

    def available_dir(self, y, x, ey, ex, bit_map):
        """
        :param y Y position in bit_map
        :param x X position in bit_map
        :param ey Exact y position
        :param ex Exact x position
        :returns array of available directions
        """

        result = AbstractDirection.available_dir(self, y, x, ey, ex, bit_map)
        if ex < x:
            result = [val for val in result if not self._is_vertical(val)]
        return result


class Right(HorizontalDirection):
    # y, x
    direction = np.array([0, 1])
    angle = 180
    opposite = EnumDirection.LEFT
    current = EnumDirection.RIGHT

    def move(self, sprite, enum_directions, dt):
        """
        moves sprite in give direction
        :param sprite Sprite to move
        :param enum_direction Direction to move in
        :param dt move multiplier
        """
        if EnumDirection.RIGHT in enum_directions:
            sprite.x += settings.MOVEMENT_SPEED * dt
            HorizontalDirection.move(self, sprite, enum_directions, dt)

    def available_dir(self, y, x, ey, ex, bit_map):
        """
        :param y Y position in bit_map
        :param x X position in bit_map
        :param ey Exact y position
        :param ex Exact x position
        :returns array of available directions
        """

        result = AbstractDirection.available_dir(self, y, x, ey, ex, bit_map)
        if ex > x:
            result = [val for val in result if not self._is_vertical(val)]
        return result


def get_direction(enum_direction):
    """
    Direction factory, creates direction from EnumDirection
    :param enum_direction EnumDirecetion of direction to get
    """

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
