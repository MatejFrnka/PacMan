from enum import Enum
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
    """
    call on colision with block
    """
    def collides(self):
        self.collect()
        return True


class FoodBlock(Block):
    def __init__(self, sprite, map):
        super().__init__(sprite)
        self.map = map

    def collect(self):
        if not self.collected:
            Block.collect(self)
            self.map.food_left -= 1
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
                self.map.kill_streak = 0


class EnumGameState(Enum):
    PLAY = 0,
    GAME_OVER = 1,
    PLAYER_DIED = 2,
    LEVEL_COMPLETE = 3,
    RESET = 4,
    STOP = 5


class Map:

    def __init__(self, bit_map):
        self.x_offset = 0
        self.y_offset = 25
        self.ghosts = []
        self.pacman = None
        self.batch = None
        self.lifes = 3
        self.lifes_img = []
        self.food_left = 0
        self.kill_streak = 0

        self.enum_game_state = EnumGameState.PLAY
        self.items = []
        self.bit_map = bit_map
        self.score = 0
        self.label_score = pyglet.text.Label('Score: ' + str(self.score),
                                             font_size=settings.BLOCK_SIZE,
                                             x=((bit_map.shape[0] + 1) * settings.BLOCK_SIZE + self.x_offset) / 2,
                                             y=(bit_map.shape[1] * settings.BLOCK_SIZE) + self.y_offset,
                                             anchor_x='center', anchor_y='bottom')
        self.label_game_over = pyglet.graphics.Batch()
        pyglet.text.Label("Game over",
                          font_size=settings.BLOCK_SIZE * 2,
                          y=(bit_map.shape[0] // 2) * settings.BLOCK_SIZE + self.y_offset,
                          x=(bit_map.shape[1] // 2) * settings.BLOCK_SIZE + self.x_offset,
                          anchor_x='center', anchor_y='bottom', batch=self.label_game_over)
        pyglet.text.Label("Press enter to restart",
                          font_size=settings.BLOCK_SIZE,
                          y=(bit_map.shape[0] // 2) * settings.BLOCK_SIZE + self.y_offset,
                          x=(bit_map.shape[1] // 2) * settings.BLOCK_SIZE + self.x_offset,
                          anchor_x='center', anchor_y='top', batch=self.label_game_over)

        self.start()

    """
    starts game
    """
    def start(self):
        print("start")
        self.batch = pyglet.graphics.Batch()
        self.food_left = 0
        self.lifes_img = []
        for life in range(self.lifes):
            spr = pyglet.sprite.Sprite(assets.pacman[0], settings.BLOCK_SIZE * (self.bit_map.shape[1] - life - 1))
            spr.scale = 0.8
            self.lifes_img.append(spr)
        self.resetPlayers()
        self.resetMap(self.bit_map)
        self.enum_game_state = EnumGameState.PLAY
    """
    reset players resets all players
    """
    def resetPlayers(self):
        print("prep players")
        self.ghosts = []
        self.enum_game_state = EnumGameState.PLAY
        self.pacman = Human(self.bit_map,
                            x_offset=self.x_offset,
                            y_offset=self.y_offset,
                            x=self.bit_map.shape[1] // 2,
                            y=self.bit_map.shape[0] // 2 - 2)
        blinky = Ghost(self.bit_map, assets.ghost_blinky,
                       self.pacman,
                       behaviour=targetbehaviour.BlinkyBehaviour(bit_map=self.bit_map, pacman=self.pacman),
                       x_offset=self.x_offset,
                       y_offset=self.y_offset)
        Timer(1, self.release, [blinky]).start()
        pinky = Ghost(self.bit_map, assets.ghost_pinky,
                      self.pacman,
                      behaviour=targetbehaviour.PinkyBehaviour(pacman=self.pacman),
                      x_offset=self.x_offset,
                      y_offset=self.y_offset)
        Timer(3, self.release, [pinky]).start()
        inky = Ghost(self.bit_map, assets.ghost_inky,
                     self.pacman,
                     behaviour=targetbehaviour.InkyBehaviour(bit_map=self.bit_map, pacman=self.pacman, blinky=blinky),
                     x_offset=self.x_offset,
                     y_offset=self.y_offset)
        Timer(4, self.release, [inky]).start()
        clyde = Ghost(self.bit_map, assets.ghost_clyde,
                      self.pacman,
                      behaviour=None,
                      x_offset=self.x_offset,
                      y_offset=self.y_offset)
        clyde.targetBehaviour = targetbehaviour.ClydeBehaviour(pacman=self.pacman, bit_map=self.bit_map, clyde=clyde)
        Timer(10, self.release, [clyde]).start()
        self.ghosts = [clyde, inky, pinky, blinky]
        # self.ghosts = [clyde]
        Timer(7, self.setScatter, [False]).start()
    """
    reset map resets map and all food on it
    """
    def resetMap(self, bit_map):
        print("create map")

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
                    self.food_left += 1
                else:
                    block = Block(None)

                items_row.append(block)
            self.items.append(items_row)
    """
    call on window update
    :arg dt is time elapsed since last update
    """
    def update(self, dt):
        if EnumGameState.RESET == self.enum_game_state:
            self.score = 0
            self.lifes = 3
            self.start()
            self.resetPlayers()
        if EnumGameState.PLAYER_DIED == self.enum_game_state:
            self.resetPlayers()
        if EnumGameState.LEVEL_COMPLETE == self.enum_game_state:
            self.start()
            self.resetPlayers()

        def set_gameState(val):
            self.enum_game_state = val

        if self.enum_game_state == EnumGameState.PLAY:
            # move human
            self.pacman.update(dt)
            # move ai
            [player.update(dt) for player in self.ghosts]

            # check collisions with food and ai
            y, x = self.pacman.getPosInMap()
            if self.items[y][x].collides():
                self.items[y][x].collect()
            # check if all food is collected
            if self.food_left == 0:
                self.enum_game_state = EnumGameState.STOP
                Timer(2, set_gameState, [EnumGameState.LEVEL_COMPLETE]).start()
            for player in self.ghosts:
                if player.collides(self.pacman):
                    if player.scared and not player.dead:
                        player.die()
                        self.kill_streak += 1
                        self.score += 200 * self.kill_streak
                    elif not player.scared and not player.dead:
                        self.lifes -= 1
                        if self.lifes == 0:
                            Timer(2, self.endGame)
                            self.pacman.die()
                            self.enum_game_state = EnumGameState.GAME_OVER
                        else:
                            self.enum_game_state = EnumGameState.STOP
                            Timer(1, set_gameState, [EnumGameState.PLAYER_DIED]).start()

        # update score lable
        self.label_score.text = 'Score: ' + str(self.score)
    """
    Sets game to ended
    """
    def endGame(self):
        self.label_game_over = True

    """
    Call on window.draw
    """
    def draw(self):
        # draw walls and food
        self.batch.draw()
        # draw human
        self.pacman.draw()
        # draw ai
        [player.draw() for player in self.ghosts]
        # draw score
        self.label_score.draw()
        if self.enum_game_state == EnumGameState.GAME_OVER:
            self.label_game_over.draw()

        for life in range(self.lifes):
            self.lifes_img[life].draw()
    """
    call on keypress
    :arg symbol pyglet.window.key
    """
    def keypress(self, symbol):
        self.pacman.keypress(symbol)
        [player.keypress(symbol) for player in self.ghosts]
        if self.enum_game_state == EnumGameState.GAME_OVER and symbol == pyglet.window.key.ENTER:
            self.enum_game_state = EnumGameState.RESET
    """
    releases ghost
    Takes reference to ghost
    """
    def release(self, ghost):
        ghost.locked = False

    """
    Sets scatter value to all ghosts
    takes value True or False
    """
    def setScatter(self, value):
        for ghost in self.ghosts:
            ghost.targetBehaviour.scatterBehaviour = value
