import numpy as np
import src.player as player

"""
Inherit this class to create behaviour for ghosts 
"""
class TargetBehaviour:
    """
    :param def_cord Default coordinates (y, x) to go to when in scatter mode
    :param pacman Reference to player pacman to chase
    """
    def __init__(self, def_cord, pacman):
        self.def_cord = def_cord
        self.pacman = pacman
        self.scatterBehaviour = True
    """
    :returns Coordinates (y, x) to go to in scatter mode
    """
    def scatter(self):
        return self.def_cord
    """
    :returns Coordinates (y, x) to go to in hunt mode
    """
    def hunt(self):
        pass
    """
    :returns Coordinates (y, x) depending on mode
    """
    def updateTarget(self):
        if self.scatterBehaviour:
            return self.scatter()
        return self.hunt()


class BlinkyBehaviour(TargetBehaviour):
    """
    :param bit_map np.array of map. More info in assetsmanager.py
    :param pacman reference to pacman
    """
    def __init__(self, bit_map, pacman):
        def_cord = np.array([-1, bit_map.shape[1] + 1])
        super().__init__(def_cord, pacman)
    """
    :returns Coordinates (y, x) to go to in hunt mode
    """
    def hunt(self):
        return self.pacman.getPosInMap()


class PinkyBehaviour(TargetBehaviour):
    """
    :param pacman reference to pacman
    """
    def __init__(self, pacman):
        def_cord = np.array([-1, -1])
        super().__init__(def_cord, pacman)
    """
    :returns Coordinates (y, x) to go to in hunt mode
    """
    def hunt(self):
        pacman_pos = np.array(self.pacman.getPosInMap())
        pacman_direction = np.array(self.pacman.direction.direction)
        result = pacman_pos + pacman_direction * 2
        return result


class InkyBehaviour(TargetBehaviour):
    """
    :param bit_map np.array of map. More info in assetsmanager.py
    :param pacman reference to pacman
    :param blinky reference to ghost with blinky behaviour
    """
    def __init__(self, bit_map, pacman, blinky):
        def_cord = np.array([bit_map.shape[0] + 1, bit_map.shape[1] + 1])
        super().__init__(def_cord, pacman)
        self.blinky = blinky
    """
    :returns Coordinates (y, x) to go to in hunt mode
    """
    def hunt(self):
        pacman_pos = np.array(self.pacman.getPosInMap())
        pacman_direction = np.array(self.pacman.direction.direction)
        anchor_point = pacman_pos + pacman_direction

        blinky_pos = np.array(self.blinky.getPosInMap())
        distance = anchor_point - blinky_pos
        result = anchor_point + distance
        return result


class ClydeBehaviour(TargetBehaviour):
    """
    :param bit_map np.array of map. More info in assetsmanager.py
    :param pacman reference to pacman
    :param clyde reference to ghost this behaviour controls
    """
    def __init__(self, bit_map, pacman, clyde):
        self.clyde = clyde
        def_cord = np.array([bit_map.shape[0] + 1, -1])
        super().__init__(def_cord, pacman)
    """
    :returns Coordinates (y, x) to go to in hunt mode
    """
    def hunt(self):
        pacman_pos = np.array(self.pacman.getPosInMap())
        clyde_pos = np.array(self.clyde.getPosInMap())
        distance = player.distance(pacman_pos, clyde_pos)

        if distance < 3:
            return TargetBehaviour.scatter(self)
        return self.pacman.getPosInMap()
