from pygame import Rect
from lib.sprite import Sprite
from dungeon.element import DungeonElement
from dungeon.element_data import ElementData
import assets


class StaticElement(DungeonElement):

    def __init__(self, data: ElementData):
        super().__init__()
        self._data = data

    @property
    def tile_id(elem) -> int:
        return elem._data.tile_id

    @property
    def image(elem):
        return assets.sprites[elem._data.image_id]

    @property
    def rect(elem) -> Rect:
        pass

    def view(elem, *args, **kwargs):
        return super().view([Sprite(
            image=elem.image,
            origin=Sprite.ORIGIN_BOTTOM,
            layer="elems",
        )], *args, **kwargs)
