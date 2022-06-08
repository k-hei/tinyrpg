import assets
from dungeon.element_static import StaticElement


class DesertBush(StaticElement):

    @property
    def tile_id(bush):
        return 2

    @property
    def tile_size(bush):
        return 16

    @property
    def image(bush):
        return assets.sprites["desert_bush"]
