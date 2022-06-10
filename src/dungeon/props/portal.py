from dungeon.props import Prop
from town.sideview.stage import Area as TownSideViewArea
from town.topview.stage import Stage as TownTopViewArea
from transits.dissolve import DissolveIn, DissolveOut


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

    def enter(portal, game):
        game.hide_label()

        if (isinstance(portal.area, type)
        and issubclass(portal.area, (TownSideViewArea, TownTopViewArea))):
            game.comps.minimap.exit()
            return game.get_head().transition(
                transits=(DissolveIn(), DissolveOut()),
                on_end=lambda: (
                    game.get_parent(cls="GameContext").load_area(portal.area)
                )
            )
        elif "Floor" in portal.area:
            return game.parent.load_floor_by_id(portal.area)
        else:
            game.comps.minimap.exit()
            return game.get_head().transition(
                transits=(DissolveIn(), DissolveOut()),
                on_end=lambda: (
                    game.parent.load_floor_by_id(portal.area)
                )
            )

    def view(portal, anims):
        return []
