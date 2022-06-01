from pygame import Rect
from lib.sprite import Sprite
import lib.vector as vector
from dungeon.element import DungeonElement
from dungeon.element_data import ElementData
import assets
from config import TILE_SIZE


class StaticElement(DungeonElement):

    def __init__(self, data: ElementData):
        super().__init__()
        self._data = data
        self.solid = data.hitbox is not None

    @property
    def tile_id(elem) -> int:
        return elem._data.tile_id

    @property
    def image(elem):
        return assets.sprites[elem._data.image_id]

    @property
    def rect(elem) -> Rect:
        try:
            return elem.__rect
        except AttributeError:
            pass

        try:
            x, y, width, height = elem._data.hitbox
            elem.__rect = Rect(
                vector.add(elem.pos, (x, y)),
                (width, height),
            )
            return elem.__rect
        except TypeError:
            # get hitbox for non-solid element
            return None

    def spawn(elem, stage, cell):
        elem.scale = TILE_SIZE
        elem.cell = vector.add(
            vector.scale(cell, 1 / 2),
            (0, -0.5),
        )

    def view(elem, *args, **kwargs):
        return super().view([Sprite(
            image=elem.image,
            origin=Sprite.ORIGIN_BOTTOM,
            layer="elems",
        )], *args, **kwargs)
