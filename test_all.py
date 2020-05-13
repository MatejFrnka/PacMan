import pytest
import src.assetsmanager as assets
import src.player
import src.map
import pyglet
import numpy as np


def map_simple():
    return np.array([[1, 1, 1, 1, 1],
                     [1, 0, 0, 0, 1],
                     [1, 0, 1, 0, 1],
                     [1, 0, 0, 0, 1],
                     [1, 1, 1, 1, 1]])


def test_assets_bit_map():
    bit_map = assets.generateMap()
    for y in range(len(bit_map)):
        for x in range(len(bit_map[y])):
            if y == 0 or y == bit_map.shape[0] - 1 or x == 0 or x == bit_map.shape[1]:
                assert bit_map[y][x] == 1


def test_map_scatter():
    test_map = src.map.Map(assets.generateMap())
    ghost1 = test_map.ghosts[0]
    test_map.setScatter(True)
    assert ghost1.targetBehaviour.scatterBehaviour
    test_map.setScatter(False)
    assert not ghost1.targetBehaviour.scatterBehaviour
    test_map.setScatter(True)
    assert ghost1.targetBehaviour.scatterBehaviour


def test_map_release():
    test_map = src.map.Map(assets.generateMap())
    ghost1 = test_map.ghosts[0]
    assert ghost1.locked
    test_map.release(ghost1)
    assert not ghost1.locked


def test_map_Block():
    block = src.map.Block(assets.wall)
    assert not block.collected
    block.collect()
    assert block.collected


def test_map_FoodBlock():
    map = src.map.Map(assets.generateMap())
    block = src.map.FoodBlock(assets.wall, map)
    assert not block.collected
    assert map.score == 0
    block.collect()
    assert block.collected
    assert map.score == 10


def test_map_SuperFoodBlock():
    map = src.map.Map(assets.generateMap())
    block = src.map.SuperFoodBlock(assets.wall, map, 10)
    assert not block.collected
    assert map.score == 0
    block.collect()
    assert block.collected
    assert map.score == 100


def test_player_collides():
    player = src.player.Human(map_simple(), 1, 1, 0, 0)
    print(player.getPosInMap())


test_player_collides()
