from threading import Timer

import pyglet
import src.assetsmanager as assets
import src.globalsettings as settings
import src.targeting as targetbehaviour
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


class SuperFoodBlock(Block):
    def __init__(self, sprite, map, scareLen):
        super().__init__(sprite)
        self.map = map
        self.scareLen = scareLen

    def collect(self):
        if not self.collected:
            Block.collect(self)
            self.map.score += 100
            for player in self.map.ghosts:
                player.scare(self.scareLen)


class Map:
    pacman_alive = True
    x_offset = 0
    y_offset = 25

    def __init__(self, bit_map):
        self.batch = pyglet.graphics.Batch()
        self.items = None
        self.human = Human(bit_map,
                           x_offset=self.x_offset,
                           y_offset=self.y_offset,
                           x=bit_map.shape[1] // 2,
                           y=bit_map.shape[0] // 2 - 2)
        blinky = Ghost(bit_map, assets.ghost_blinky,
                       self.human,
                       behaviour=targetbehaviour.BlinkyBehaviour(bit_map=bit_map, pacman=self.human),
                       x_offset=self.x_offset,
                       y_offset=self.y_offset)
        Timer(1, self.release, [blinky]).start()
        pinky = Ghost(bit_map, assets.ghost_pinky,
                      self.human,
                      behaviour=targetbehaviour.PinkyBehaviour(pacman=self.human),
                      x_offset=self.x_offset,
                      y_offset=self.y_offset)
        Timer(3, self.release, [pinky]).start()
        inky = Ghost(bit_map, assets.ghost_inky,
                     self.human,
                     behaviour=targetbehaviour.InkyBehaviour(bit_map=bit_map, pacman=self.human, blinky=blinky),
                     x_offset=self.x_offset,
                     y_offset=self.y_offset)
        Timer(4, self.release, [inky]).start()
        clyde = Ghost(bit_map, assets.ghost_clyde,
                      self.human,
                      behaviour=None,
                      x_offset=self.x_offset,
                      y_offset=self.y_offset)
        Timer(10, self.release, [clyde]).start()
        clyde.targetBehaviour = targetbehaviour.ClydeBehaviour(pacman=self.human, bit_map=bit_map, clyde=clyde)

        self.ghosts = [clyde, inky, pinky, blinky]
        self.score = 0
        self.leftToCollect = 0
        self.createMap(bit_map)
        self.scoreLabel = pyglet.text.Label('Score: ' + str(self.score),
                                            font_size=settings.BLOCK_SIZE,
                                            x=((bit_map.shape[0] + 1) * settings.BLOCK_SIZE + self.x_offset) / 2,
                                            y=(bit_map.shape[1] * settings.BLOCK_SIZE) + self.y_offset,
                                            anchor_x='center', anchor_y='bottom')
        self.setScatter(True)
        Timer(9, self.setScatter, [False]).start()

    def update(self, dt):
        if self.pacman_alive:
            # move human
            self.human.update(dt)
            # move ai
            [player.update(dt) for player in self.ghosts]

            # check collisions with food and ai
            y, x = self.human.getPosInMap()
            if self.items[y][x].collides(y, x):
                self.items[y][x].collect()
            # check if all food is collected
            if self.leftToCollect == 0:
                ...  # win
            for player in self.ghosts:
                if player.collides(self.human):
                    if player.scared:
                        player.die()
                    elif not player.scared and not player.dead:
                        self.pacman_alive = False
                        self.human.die()

        # update score lable
        self.scoreLabel.text = 'Score: ' + str(self.score)

    def draw(self):
        # draw walls and food
        self.batch.draw()
        # draw human
        self.human.draw()
        # draw ai
        [player.draw() for player in self.ghosts]
        # draw score
        self.scoreLabel.draw()

    def keypress(self, symbol):
        self.human.keypress(symbol)
        [player.keypress(symbol) for player in self.ghosts]

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
                    block = SuperFoodBlock(sprite, self, 5)
                # FOOD
                elif bit_map[y][x] == 9:
                    sprite = make_sprite(x, y, assets.food_small)
                    block = FoodBlock(sprite, self)
                    self.leftToCollect += 1
                else:
                    block = Block(None)

                items_row.append(block)
            self.items.append(items_row)

    def release(self, ghost):
        ghost.locked = False

    def setScatter(self, value):
        for ghost in self.ghosts:
            ghost.targetBehaviour.scatterBehaviour = value
