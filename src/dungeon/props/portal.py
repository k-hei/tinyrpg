from dungeon.props import Prop
from town.sideview.stage import Area as TownSideViewArea
from town.topview.stage import Stage as TownTopViewArea
from config import LABEL_FRAMES


class Portal(Prop):

    def __init__(portal, area, *args, port=None, name="", **kwargs):
        super().__init__(*args, **kwargs)
        portal.area = area
        portal.port = port
        portal.name = name

    def effect(portal, game, trigger, *args, **kwargs):
        if trigger != game.hero:
            return False

        game.parent.time += LABEL_FRAMES  # HACK: force hide auto-label (can we clean this up?)
        game.show_label(portal.name or portal.area)
        return True

    def on_leave(portal, game):
        game.hide_label()

    def enter(portal, game):
        game.hide_label()

        if (isinstance(portal.area, type)
        and issubclass(portal.area, (TownSideViewArea, TownTopViewArea))):
            game.comps.minimap.exit()
            return game.get_head().transition(on_end=lambda: (
                game.get_parent(cls="GameContext").load_area(portal.area)
            ))
        elif "Floor" in portal.area:
            return game.parent.load_floor_by_id(portal.area)
        else:
            game.comps.minimap.exit()
            return game.get_head().transition(on_end=lambda: (
                game.parent.load_floor_by_id(portal.area, portal.port)
            ))

    def view(portal, anims):
        return []
