from pygame import Rect
from dungeon.props import Prop
import lib.vector as vector
from config import TILE_SIZE


class Portal(Prop):

    def __init__(portal, area, *args, port=None, name="", **kwargs):
        super().__init__(*args, **kwargs)
        portal.area = area
        portal.port = port
        portal.name = name

    def effect(portal, game, *_):
        game.show_label(portal.name or portal.area)

    def on_leave(portal, game):
        game.hide_label()

    def view(portal, anims):
        return []
