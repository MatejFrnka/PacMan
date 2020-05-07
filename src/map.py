import pyglet
import src.assetsmanager as assets
import src.globalsettings as settings

class Map:
    def __init__(self, bit_map):
        self.batch = pyglet.graphics.Batch()
        self.map = self.createMap(bit_map)

    def draw(self):
        self.batch.draw()

    def createMap(self, bit_map):
        res = []
        for y in range(bit_map.shape[0]):
            for x in range(bit_map.shape[1]):

                if bit_map[y][x] != 0:
                    sprite = pyglet.sprite.Sprite(assets.wall, x=x * settings.BLOCK_SIZE,
                                                  y=y * settings.BLOCK_SIZE,
                                                  batch=self.batch)
                    sprite.scale = settings.BLOCK_SIZE / sprite.height
                    res.append(sprite)
        return res