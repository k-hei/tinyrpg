from contexts import Context
from town.graph import TownGraph
from town.areas.central import CentralArea
from town.areas.clearing import ClearingArea
from town.areas.outskirts import OutskirtsArea
from town.areas.store import StoreArea
from town.areas.fortune import FortuneArea
from town.sideview.context import SideViewContext
from town.sideview.stage import Area as SideViewArea
from town.topview.context import TopViewContext
from town.topview.stage import Stage as TopViewArea
from dungeon.context import DungeonContext
from cores.knight import Knight
from cores.mage import Mage

class TownContext(Context):
  def __init__(ctx, store, returning=False):
    super().__init__()
    ctx.store = store
    ctx.returning = returning
    ctx.area = OutskirtsArea
    ctx.graph = TownGraph(
      nodes=[CentralArea, ClearingArea, OutskirtsArea, FortuneArea, StoreArea],
      edges=[
        (CentralArea.links["door_triangle"], StoreArea.links["entrance"]),
        (CentralArea.links["door_heart"], FortuneArea.links["entrance"]),
        (CentralArea.links["alley"], ClearingArea.links["alley"]),
        (CentralArea.links["right"], OutskirtsArea.links["left"]),
        (OutskirtsArea.links["tower"], DungeonContext),
      ]
    )

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
