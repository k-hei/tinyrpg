from contexts import Context
from contexts.dungeon import DungeonContext
from town.areas.akimor_central import AkimorCentralArea
from town.sideview.context import SideViewContext
from town.sideview.stage import Area as SideViewArea
from town.topview.context import TopViewContext
from town.topview.stage import Stage as TopViewArea

class TownContext(Context):
    def __init__(ctx, store):
        super().__init__()
        ctx.store = store
        ctx.area = AkimorCentralArea

    @property
    def graph(ctx):
        return ctx.parent.graph

    def init(ctx):
        ctx.load_area(ctx.area)

    def load_area(ctx, area, link=None):
        for char in ctx.store.party:
            char.anims.clear()

        if area is DungeonContext:
            return ctx.parent.goto_dungeon()

        if issubclass(area, SideViewArea):
            child = SideViewContext(store=ctx.store, area=area, spawn=link)
        elif issubclass(area, TopViewArea):
            child = TopViewContext(store=ctx.store, area=area, spawn=link)
        ctx.open(child)
