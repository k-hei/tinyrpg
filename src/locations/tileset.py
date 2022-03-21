from abc import ABC, abstractmethod
from pygame import Surface


class Tileset(ABC):

    @staticmethod
    def is_tile_solid(tile):
        return False

    @staticmethod
    def is_tile_pit(tile):
        return False

    @staticmethod
    def is_tile_hallway(tile):
        return False

    @staticmethod
    def is_tile_oasis(tile):
        return False

    @staticmethod
    def is_tile_link(tile):
        return False

    @abstractmethod
    def render_tile(tile) -> Surface:
        pass
