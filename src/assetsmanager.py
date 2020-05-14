import pyglet
import numpy as np
from enum import Enum

PACMAN = pyglet.image.ImageGrid(pyglet.image.load('assets/players/pacman.png'), 1, 9, column_padding=4)
GHOTS_BLINKY = pyglet.image.ImageGrid(pyglet.image.load('assets/players/blinky.png'), 1, 8, column_padding=4)
GHOST_PINKY = pyglet.image.ImageGrid(pyglet.image.load('assets/players/pinky.png'), 1, 8, column_padding=4)
GHOST_INKY = pyglet.image.ImageGrid(pyglet.image.load('assets/players/inky.png'), 1, 8, column_padding=4)
GHOST_CLYDE = pyglet.image.ImageGrid(pyglet.image.load('assets/players/clyde.png'), 1, 8, column_padding=4)
GHOST_EYES = pyglet.image.ImageGrid(pyglet.image.load('assets/players/eyes.png'), 1, 8, column_padding=4)
WALL = pyglet.image.load('assets/wall.png')
FOOD_SMALL = pyglet.image.load('assets/food_small.png')
FOOD_LARGE = pyglet.image.load('assets/food_large.png')


def get_pos(direction):
    if EnumDirection.RIGHT == direction:
        dir_pos = 0
    elif EnumDirection.DOWN == direction:
        dir_pos = 1
    elif EnumDirection.LEFT == direction:
        dir_pos = 2
    else:
        dir_pos = 3
    return dir_pos


def get_scared(ending):
    ghost = pyglet.image.ImageGrid(pyglet.image.load('assets/players/scared.png'), 1, 4, column_padding=4)
    amount = 4 if ending else 2
    return pyglet.image.Animation.from_image_sequence([ghost[img] for img in range(amount)], 0.1, True)


def get_pacman(direction):
    dir_pos = get_pos(direction)
    img_cnt = 2
    img_seq = [PACMAN[dir_pos * img_cnt + img] for img in range(img_cnt)]
    img_seq.append(PACMAN[8])
    return pyglet.image.Animation.from_image_sequence(img_seq, 0.1, True)


def get_ghost(direction, ghost):
    dir_pos = get_pos(direction)
    img_cnt = 2
    return pyglet.image.Animation.from_image_sequence([ghost[dir_pos * img_cnt + img] for img in range(img_cnt)], 0.1, True)


class EnumDirection(Enum):
    STOP = 0
    UP = 1
    DOWN = -1
    LEFT = -2
    RIGHT = 2


def generate_map():
    """
    Creates a map. Type of 2d np.array
    Value 0 = Empty space
    Value 1 = Wall
    Value 2 = Super food
    Value 9 = Food
    """
    # top left corner of map
    topLeft = np.array([
        [1, 9, 9, 9, 9, 9, 9, 9, 9, 1],
        [1, 2, 1, 1, 9, 1, 1, 1, 9, 1],
        [1, 9, 9, 9, 9, 9, 9, 9, 9, 9],
        [1, 9, 1, 1, 9, 1, 9, 1, 1, 1],
        [1, 9, 9, 9, 9, 1, 9, 9, 9, 1],
        [1, 9, 1, 1, 9, 1, 1, 1, 0, 1],
        [1, 9, 1, 1, 9, 1, 0, 0, 0, 0],
        [1, 9, 1, 1, 9, 1, 0, 1, 1, 3],
        [1, 9, 1, 1, 9, 0, 0, 1, 0, 0],
    ])
    width = topLeft.shape[1] * 2 - 1
    # add top border
    res = np.array([1 for i in range(width)])
    for i in range(topLeft.shape[0]):
        res = np.vstack((res, np.append(topLeft[i][0:-1], topLeft[i][::-1])))
    res = np.vstack((res[:-1], res[::-1]))
    res[10, 9] = 1
    return res
