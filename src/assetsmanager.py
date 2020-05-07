import pyglet
import numpy as np
import src.globalsettings as settings

pacman = pyglet.image.load_animation('assets/pacman.gif')
wall = pyglet.image.load('assets/wall.png')


def generateMap():
    topLeft = np.array([
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 0, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [1, 0, 1, 1, 0, 1, 0, 1, 1, 1],
        [1, 0, 0, 0, 0, 1, 0, 0, 0, 1],
        [1, 1, 1, 1, 0, 1, 1, 1, 0, 1],
        [0, 0, 0, 1, 0, 1, 0, 0, 0, 0],
        [1, 1, 1, 1, 0, 1, 0, 1, 1, 3],
        [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    ])
    width = topLeft.shape[1] * 2 - 1
    # add top border
    res = np.array([1 for i in range(width)])
    for i in range(topLeft.shape[0]):
        res = np.vstack((res, np.append(topLeft[i][0:-1], topLeft[i][::-1])))

    return np.vstack((res[:-1], res[::-1]))
