from contexts import Context
from town.graph import TownGraph
from town.areas.central import CentralArea
from town.areas.clearing import ClearingArea
from town.areas.store import StoreArea
from town.areas.fortune import FortuneArea
from town.sideview.context import SideViewContext
from town.sideview.stage import Area as SideViewArea
from town.topview.context import TopViewContext
from town.topview.stage import Stage as TopViewArea
from cores.knight import Knight

class TownContext(Context):
  def __init__(ctx, party=[]):
    super().__init__()
    ctx.party = party or [Knight(facing=(0, 1))]
    ctx.area = ClearingArea
    ctx.graph = TownGraph(
      nodes=[CentralArea, ClearingArea, FortuneArea, StoreArea],
      edges=[
        (CentralArea.links["door_triangle"], StoreArea.links["entrance"]),
        (CentralArea.links["door_heart"], FortuneArea.links["entrance"]),
        (CentralArea.links["alley"], ClearingArea.links["alley"]),
      ]
    )

  def init(ctx):
    ctx.load_area(ctx.area)

  def load_area(ctx, area, link=None):
    if issubclass(area, SideViewArea):
      child = SideViewContext(area, ctx.graph, ctx.party, link)
    elif issubclass(area, TopViewArea):
      child = TopViewContext(area, ctx.party, link)
    ctx.open(child)
