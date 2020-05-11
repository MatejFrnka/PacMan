import numpy as np


class TargetBehaviour:
    # def cord is in format y, x
    def __init__(self, def_cord, pacman):
        self.def_cord = def_cord
        self.pacman = pacman

    scatterBehaviour = True

    def scatter(self):
        return self.def_cord

    def hunt(self):
        pass

    def updateTarget(self):
        if self.scatterBehaviour:
            return self.scatter()
        return self.hunt()


class BlinkyBehaviour(TargetBehaviour):
    def __init__(self, bit_map, pacman):
        def_cord = np.array([-1, bit_map.shape[1] + 1])
        super().__init__(def_cord, pacman)

    def hunt(self):
        return self.pacman.getPosInMap()


class PinkyBehaviour(TargetBehaviour):
    def __init__(self, pacman):
        def_cord = np.array([-1, -1])
        super().__init__(def_cord, pacman)

    def hunt(self):
        pacman_pos = np.array(self.pacman.getPosInMap())
        pacman_direction = np.array(self.pacman.direction.direction)
        result = pacman_pos + pacman_direction * 2
        return result


class InkyBehaviour(TargetBehaviour):
    def __init__(self, bit_map, pacman, blinky):
        def_cord = np.array([bit_map.shape[0] + 1, bit_map.shape[1] + 1])
        super().__init__(def_cord, pacman)
        self.blinky = blinky

    def hunt(self):
        pacman_pos = np.array(self.pacman.getPosInMap())
        pacman_direction = np.array(self.pacman.direction.direction)
        anchor_point = pacman_pos + pacman_direction

        blinky_pos = np.array(self.blinky.getPosInMap())
        distance = anchor_point - blinky_pos
        result = anchor_point + distance
        return result


class ClydeBehaviour(TargetBehaviour):
    def __init__(self, bit_map, pacman):
        def_cord = np.array([bit_map.shape[0] + 1, -1])
        super().__init__(def_cord, pacman)

    def hunt(self):
        return self.pacman.getPosInMap()
