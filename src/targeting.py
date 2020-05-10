import numpy as np


class TargetBehaviour:
    def updateTarget(self, pacman):
        pass


class BlinkyBehaviour:
    def updateTarget(self, pacman):
        return pacman.getPosInMap()


class PinkyBehaviour:
    def updateTarget(self, pacman):
        pacman_pos = np.array(pacman.getPosInMap())
        pacman_direction = np.array(pacman.direction.direction)
        result = pacman_pos + pacman_direction * 4
        return result
