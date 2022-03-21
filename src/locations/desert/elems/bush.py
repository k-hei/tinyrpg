from lib.sprite import Sprite
import assets
from dungeon.element import DungeonElement as Element


TILE_SIZE = 16
image = assets.sprites["desert_bush"]


class DesertBush(Element):

    tile_id = 2
    size = (image.get_width() // TILE_SIZE, image.get_height() // TILE_SIZE)

    def view(bush, *args, **kwargs):
        return super().view([Sprite(
            image=assets.sprites["desert_bush"],
            pos=(-16, 16),
            origin=Sprite.ORIGIN_BOTTOM,
            layer="elems",
        )], *args, **kwargs)
