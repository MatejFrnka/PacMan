import pyglet
import src.assetsmanager as assets
import src.globalsettings as settings


class Block:
    def __init__(self, sprite):
        self.sprite = sprite
        self.collected = False

    def collect(self):
        self.sprite.opacity = 0
        print("a")

    def collides(self, y, x):
        # Todo: IMPLEMENT COLLISION SYSTEM
        if not self.collected:
            self.collected = True
            return True
        return False


class Map:
    def __init__(self, bit_map, human, players=None):
        if (players is None):
            players = []
        self.batch = pyglet.graphics.Batch()
        self.items = None
        self.createMap(bit_map)
        self.human = human
        self.players = players

    def update(self, dt):
        # TODO:REPLACE 0.016 WITH DT!!!
        self.human.update(0.016)
        [player.update(dt) for player in self.players]

        y, x = self.human.getPosInMap()
        if self.items[y][x].collides(y, x):
            self.items[y][x].collect()

    def draw(self):
        self.batch.draw()
        self.human.draw()
        [player.draw() for player in self.players]

    def keypress(self, symbol):
        self.human.keypress(symbol)
        [player.keypress(symbol) for player in self.players]

    def createMap(self, bit_map):
        def calc_y(y):
            return bit_map.shape[0] - y - 1

        def make_sprite(x, y, img):
            sprite = pyglet.sprite.Sprite(img,
                                          x=x * settings.BLOCK_SIZE,
                                          y=calc_y(y) * settings.BLOCK_SIZE,
                                          batch=self.batch)
            sprite.scale = settings.BLOCK_SIZE / sprite.height
            return sprite

        self.items = []

        for y in range(bit_map.shape[0]):
            items_row = []
            for x in range(bit_map.shape[1]):
                sprite = None
                if bit_map[y][x] == 1:
                    sprite = make_sprite(x, y, assets.wall)
                if bit_map[y][x] == 2:
                    sprite = make_sprite(x, y, assets.food_large)
                elif bit_map[y][x] == 9:
                    sprite = make_sprite(x, y, assets.food_small)
                items_row.append(Block(sprite))
            self.items.append(items_row)
