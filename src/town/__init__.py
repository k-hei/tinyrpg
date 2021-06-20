from contexts import Context
from town.graph import TownGraph
from town.areas.store import StoreArea
from town.areas.central import CentralArea
from town.sideview.stage import Area as SideViewArea
from town.sideview import SideViewContext
from town.topview.stage import Stage as TopViewArea
from town.topview import TopViewContext
from cores.knight import KnightCore

class TownContext(Context):
  def __init__(ctx, party=[]):
    super().__init__()
    ctx.party = party or [KnightCore()]
    ctx.area = CentralArea
    ctx.graph = TownGraph(
      nodes=[CentralArea, StoreArea],
      edges=[
        (CentralArea.links["door_heart"], StoreArea.links["entrance"]),
      ]
    )

  def init(ctx):
    ctx.load_area(ctx.area)

  def load_area(ctx, area, link=None):
    if issubclass(area, SideViewArea):
      child = SideViewContext(area, ctx.party, link)
    elif issubclass(area, TopViewArea):
      child = TopViewContext(area, ctx.party, link)
    ctx.open(child)
