from abc import ABC, abstractmethod
from lib.sprite import Sprite
from dungeon.element import DungeonElement


class StaticElement(DungeonElement, ABC):

    @abstractmethod
    def tile_id(elem) -> int:
        pass

    @abstractmethod
    def tile_size(elem) -> int:
        pass

    @abstractmethod
    def image(elem):
        pass

    @property
    def size(elem) -> tuple[int, int]:
        return (
            elem.image.get_width() // elem.tile_size,
            elem.image.get_height() // elem.tile_size,
        )

    def view(elem, *args, **kwargs):
        return super().view([Sprite(
            image=elem.image,
            origin=Sprite.ORIGIN_BOTTOM,
            layer="elems",
        )], *args, **kwargs)
