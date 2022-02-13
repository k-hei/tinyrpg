from contexts import Context
from town.graph import TownGraph
from town.areas.akimor_central import AkimorCentralArea
from town.areas.fortune import FortuneArea
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
    ctx.area = AkimorCentralArea
    ctx.graph = TownGraph(
      nodes=[AkimorCentralArea, FortuneArea],
      edges=[
        (AkimorCentralArea.links["upper_slope_top"], AkimorCentralArea.links["upper_slope_base"]),
        (AkimorCentralArea.links["lower_slope_top"], AkimorCentralArea.links["lower_slope_base"]),
        (AkimorCentralArea.links["fortune_house"], FortuneArea.links["entrance"]),
      ]
    )

  def init(ctx):
    link = None # OutskirtsArea.links["tower"] if ctx.returning else None
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
