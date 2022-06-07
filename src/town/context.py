from contexts import Context
from contexts.dungeon import DungeonContext
from town.sideview.context import SideViewContext
from town.sideview.stage import Area as SideViewArea
from town.topview.context import TopViewContext
from town.topview.stage import Stage as TopViewArea

from town.areas.akimor_central import AkimorCentralArea


class TownContext(Context):
    def __init__(ctx, store, area=None, port=None):
        super().__init__()
        ctx.store = store
        ctx.area = area or AkimorCentralArea
        ctx.port = port

    @property
    def graph(ctx):
        return ctx.parent.graph

    def init(ctx):
        ctx.store.restore_party()
        ctx.load_area(ctx.area, ctx.port)

    def load_area(ctx, area, port=None):
        for char in ctx.store.party:
            char.anims.clear()

        if area is DungeonContext:
            return ctx.parent.goto_dungeon()

        port = area.ports[port] if port else None
        if issubclass(area, SideViewArea):
            child = SideViewContext(store=ctx.store, area=area, spawn=port)
        elif issubclass(area, TopViewArea):
            child = TopViewContext(store=ctx.store, area=area, spawn=port)

        ctx.open(child)
