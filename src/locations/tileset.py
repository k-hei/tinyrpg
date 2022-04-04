import json
from abc import ABC, abstractmethod
from pygame import Surface
from dungeon.element_static import StaticElement
from dungeon.element_data import ElementData
import assets


class Tileset(ABC):
    tile_size = 16

    @classmethod
    def _preinit_elem_data(cls, elem_data):
        elem_image_id = elem_data["image_id"]
        elem_image = assets.sprites[elem_image_id]
        elem_cols = elem_image.get_width() // cls.tile_size
        elem_rows = elem_image.get_height() // cls.tile_size
        return {
            "size": (elem_cols, elem_rows),
            **elem_data
        }

    @classmethod
    @property
    def _elems(cls):
        try:
            return cls.__elems
        except AttributeError:
            pass

        with open(cls.elems_path, mode="r", encoding="utf-8") as file:
            file_buffer = file.read()

        file_data = json.loads(file_buffer)
        cls.__elems = {
            elem["name"]: ElementData(**cls._preinit_elem_data(elem))
                for elem in file_data
        }
        return cls.__elems

    @classmethod
    def resolve_elem(cls, elem_name):
        elem_data = cls._elems[elem_name]
        return lambda **elem_props: StaticElement(elem_data, **elem_props)

    @staticmethod
    def is_tile_solid(tile):
        return False

    @staticmethod
    def is_tile_opaque(tile):
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
