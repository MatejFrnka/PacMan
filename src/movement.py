from abc import ABC
from src.assetsmanager import Direction
import src.globalsettings as settings


class AbstractDirection(ABC):
    vertical = None
    epsilon = 0.1

    def move(self, sprite, direction, dt):
        pass

    def round(self, sprite, dt):
        pass


class VerticalDirection(AbstractDirection):
    vertical = True

    def move(self, sprite, direction, dt):
        dif = (round(sprite.x / settings.BLOCK_SIZE) * settings.BLOCK_SIZE) - sprite.x
        if dif > self.epsilon:
            sprite.x += settings.MOVEMENT_SPEED * dt * abs(dif / 5)
        elif dif < self.epsilon:
            sprite.x -= settings.MOVEMENT_SPEED * dt * abs(dif / 5)


class HorizontalDirection(AbstractDirection):
    vertical = False

    def move(self, sprite, direction, dt):
        dif = (round(sprite.y / settings.BLOCK_SIZE) * settings.BLOCK_SIZE) - sprite.y
        if dif > self.epsilon:
            sprite.y += settings.MOVEMENT_SPEED * dt * abs(dif / 5)
        elif dif < self.epsilon:
            sprite.y -= settings.MOVEMENT_SPEED * dt * abs(dif / 5)


class Stop(AbstractDirection):
    def move(self, sprite, direction, distance):
        return


class Up(VerticalDirection):
    def move(self, sprite, directions, dt):
        if Direction.UP in directions:
            sprite.y += settings.MOVEMENT_SPEED * dt
            VerticalDirection.move(self, sprite, directions, dt)


class Down(VerticalDirection):

    def move(self, sprite, directions, dt):
        if Direction.DOWN in directions:
            sprite.y -= settings.MOVEMENT_SPEED * dt
            VerticalDirection.move(self, sprite, directions, dt)


class Left(HorizontalDirection):

    def move(self, sprite, directions, dt):
        if Direction.LEFT in directions:
            sprite.x -= settings.MOVEMENT_SPEED * dt
            HorizontalDirection.move(self, sprite, directions, dt)


class Right(HorizontalDirection):

    def move(self, sprite, directions, dt):
        if Direction.RIGHT in directions:
            sprite.x += settings.MOVEMENT_SPEED * dt
            HorizontalDirection.move(self, sprite, directions, dt)


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
