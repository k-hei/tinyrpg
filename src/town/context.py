from contexts import Context
from town.graph import WorldGraph
from town.areas.time_chamber import TimeChamberArea
from town.areas.akimor_central import AkimorCentralArea
from town.areas.fortune import FortuneArea
from town.areas.store import StoreArea as MarketArea
from town.areas.outskirts import OutskirtsArea
from town.sideview.context import SideViewContext
from town.sideview.stage import Area as SideViewArea
from town.topview.context import TopViewContext
from town.topview.stage import Stage as TopViewArea
from contexts.dungeon import DungeonContext

class TownContext(Context):
  def __init__(ctx, store, returning=False):
    super().__init__()
    ctx.store = store
    ctx.returning = returning
    ctx.area = OutskirtsArea if returning else AkimorCentralArea

  @property
  def graph(ctx):
    return ctx.parent.graph

  def init(ctx):
    link = OutskirtsArea.links["tower"] if ctx.returning else None
    ctx.load_area(ctx.area, link)

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
