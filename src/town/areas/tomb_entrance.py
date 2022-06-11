import lib.vector as vector
from lib.line import connect_lines
from lib.sprite import Sprite

from town.sideview.stage import Area, AreaPort, AreaBgLayer
import assets


CAMERA_OFFSET = (0, -36)
BG_LAYERGROUP_OFFSET = (160, -164)

class TombEntranceArea(Area):
    name = "Tomb Entrance"

    bg = [
        AreaBgLayer(sprite=Sprite(
            image=assets.sprites["tomb_entrance_building"],
            layer="bg",
            pos=BG_LAYERGROUP_OFFSET,
        )),
        AreaBgLayer(sprite=Sprite(
            image=assets.sprites["tomb_entrance_stairs"],
            layer="elems",
            offset=assets.sprites["tomb_entrance_stairs"].get_height(),
            pos=vector.add(
                BG_LAYERGROUP_OFFSET,
                (-160, assets.sprites["tomb_entrance_building"].get_height() - 72),
            ),
        )),
    ]

    camera_offset = CAMERA_OFFSET

    ports = {
        "town": AreaPort(x=448, y=0, direction=(0, 1)),
    }

    geometry = [
        *connect_lines([(144, 0), (752, 0)]),
    ]
