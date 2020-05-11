import pyglet
import src.assetsmanager as assets
import src.globalsettings as settings
import src.targeting as TargetBehaviour
from src.player import Human, Ghost


class Block:
    def __init__(self, sprite):
        self.sprite = sprite
        self.collected = False

    def collect(self):
        if not self.collected:
            if self.sprite is not None:
                self.sprite.opacity = 0
            self.collected = True

    def collides(self, y, x):
        self.collect()
        # Todo: IMPLEMENT COLLISION SYSTEM
        return True


class FoodBlock(Block):
    def __init__(self, sprite, map):
        super().__init__(sprite)
        self.map = map

    def collect(self):
        if not self.collected:
            Block.collect(self)
            self.map.leftToCollect -= 1
            self.map.score += 10


class Map:
    x_offset = 0
    y_offset = 25

    def __init__(self, bit_map):
        self.batch = pyglet.graphics.Batch()
        self.items = None
        self.human = Human(bit_map, x_offset=self.x_offset, y_offset=self.y_offset)
        blinky = Ghost(bit_map, assets.ghost_blinky,
                       self.human,
                       behaviour=TargetBehaviour.BlinkyBehaviour(bit_map=bit_map, pacman=self.human),
                       x_offset=self.x_offset,
                       y_offset=self.y_offset)
        pinky = Ghost(bit_map, assets.ghost_pinky,
                      self.human,
                      behaviour=TargetBehaviour.PinkyBehaviour(pacman=self.human),
                      x_offset=self.x_offset,
                      y_offset=self.y_offset)
        inky = Ghost(bit_map, assets.ghost_inky,
                     self.human,
                     behaviour=TargetBehaviour.InkyBehaviour(bit_map=bit_map, pacman=self.human, blinky=blinky),
                     x_offset=self.x_offset,
                     y_offset=self.y_offset)
        clyde = Ghost(bit_map, assets.ghost_clyde,
                      self.human,
                      behaviour=TargetBehaviour.ClydeBehaviour(pacman=self.human, bit_map=bit_map),
                      x_offset=self.x_offset,
                      y_offset=self.y_offset)

        self.players = [blinky, pinky, inky, clyde]
        self.score = 0
        self.leftToCollect = 0
        self.createMap(bit_map)
        self.scoreLabel = pyglet.text.Label('Score: ' + str(self.score),
                                            font_size=settings.BLOCK_SIZE,
                                            x=((bit_map.shape[0] + 1) * settings.BLOCK_SIZE + self.x_offset) / 2,
                                            y=(bit_map.shape[1] * settings.BLOCK_SIZE) + self.y_offset,
                                            anchor_x='center', anchor_y='bottom')

    def update(self, dt):
        # TODO: REMOVE ONLY FOR DEBUGGING
        dt = 0.016
        # move human

        self.human.update(dt)
        # move ai
        [player.update(dt) for player in self.players]

        # check collisions with food and ai
        y, x = self.human.getPosInMap()
        if self.items[y][x].collides(y, x):
            self.items[y][x].collect()
        if self.leftToCollect == 0:
            ...
        # update score lable
        self.scoreLabel.text = 'Score: ' + str(self.score)

    def draw(self):
        # draw walls and food
        self.batch.draw()
        # draw human
        self.human.draw()
        # draw ai
        [player.draw() for player in self.players]
        # draw score
        self.scoreLabel.draw()

    def keypress(self, symbol):
        self.human.keypress(symbol)
        [player.keypress(symbol) for player in self.players]

    def createMap(self, bit_map):

        def make_sprite(x, y, img):
            sprite = pyglet.sprite.Sprite(img,
                                          x=x * settings.BLOCK_SIZE + self.x_offset,
                                          y=(bit_map.shape[0] - y - 1) * settings.BLOCK_SIZE + self.y_offset,
                                          batch=self.batch)
            sprite.scale = settings.BLOCK_SIZE / sprite.height
            return sprite

        self.items = []

        for y in range(bit_map.shape[0]):
            items_row = []
            for x in range(bit_map.shape[1]):
                block = None
                # WALL
                if bit_map[y][x] == 1:
                    sprite = make_sprite(x, y, assets.wall)
                    block = Block(sprite)
                # SUPER FOOD
                elif bit_map[y][x] == 2:
                    sprite = make_sprite(x, y, assets.food_large)
                    block = Block(sprite)
                # FOOD
                elif bit_map[y][x] == 9:
                    sprite = make_sprite(x, y, assets.food_small)
                    block = FoodBlock(sprite, self)
                    self.leftToCollect += 1
                else:
                    block = Block(None)

                items_row.append(block)
            self.items.append(items_row)
