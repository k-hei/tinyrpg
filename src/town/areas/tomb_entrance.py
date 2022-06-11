import lib.vector as vector
from lib.line import connect_lines
from lib.sprite import Sprite

from town.element import Element
from town.sideview.stage import Area, AreaPort, AreaBgLayer
import assets


CAMERA_OFFSET = (0, -20)
BG_LAYERGROUP_OFFSET = (160, -164)
BG_FLOOR_OFFSET_Y = assets.sprites["tomb_entrance_building"].get_height() - 108

class TombEntranceArea(Area):
    name = "Tomb Entrance"

    bg = [
        AreaBgLayer(sprite=Sprite(
            image=assets.sprites["tomb_entrance_building"],
            layer="bg",
            pos=vector.add(
                BG_LAYERGROUP_OFFSET,
                (0, 120)
            ),
        ), scaling=(1, 1 / 2), offset=(0, -72)),
        AreaBgLayer(sprite=Sprite(
            image=assets.sprites["tomb_entrance_stairs"],
            layer="bg",
            pos=vector.add(
                BG_LAYERGROUP_OFFSET,
                (-160, assets.sprites["tomb_entrance_building"].get_height()),
            ),
        )),
        AreaBgLayer(sprite=Sprite(
            image=assets.sprites["tomb_entrance_stairs_statues"],
            layer="fg",
            pos=vector.add(
                BG_LAYERGROUP_OFFSET,
                (-160, assets.sprites["tomb_entrance_building"].get_height() - 72),
            ),
        )),
    ]

    elems = [
        Element(sprite=Sprite(
            image=assets.sprites["tomb_entrance_boxes"],
            pos=vector.add(
                BG_LAYERGROUP_OFFSET,
                (176, BG_FLOOR_OFFSET_Y),
            ),
            origin=Sprite.ORIGIN_BOTTOMLEFT,
            layer="bg",
        )),
        Element(sprite=Sprite(
            image=assets.sprites["tomb_entrance_banner_left"],
            pos=vector.add(
                BG_LAYERGROUP_OFFSET,
                (224, BG_FLOOR_OFFSET_Y - 96),
            ),
            origin=Sprite.ORIGIN_TOPLEFT,
            layer="bg",
        )),
        Element(sprite=Sprite(
            image=assets.sprites["tomb_entrance_banner_right"],
            pos=vector.add(
                BG_LAYERGROUP_OFFSET,
                (320, BG_FLOOR_OFFSET_Y - 96),
            ),
            origin=Sprite.ORIGIN_TOPLEFT,
            layer="bg",
        )),
        Element(sprite=Sprite(
            image=assets.sprites["tomb_entrance_sign"],
            pos=vector.add(
                BG_LAYERGROUP_OFFSET,
                (320, BG_FLOOR_OFFSET_Y - 64),
            ),
            origin=Sprite.ORIGIN_TOPLEFT,
            layer="bg",
        )),
    ]

    camera_offset = CAMERA_OFFSET
    camera_does_lock = False

    ports = {
        "dungeon": AreaPort(x=448, y=0, direction=(0, -1), lock_camera=True),
        "town": AreaPort(x=448, y=0, direction=(0, 1)),
    }

    geometry = [
        *connect_lines([(144, 0), (752, 0)]),
    ]
