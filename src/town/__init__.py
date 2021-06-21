from contexts import Context
from town.graph import TownGraph
from town.areas.central import CentralArea
from town.areas.store import StoreArea
from town.areas.fortune import FortuneArea
from town.sideview.context import SideViewContext
from town.sideview.stage import Area as SideViewArea
from town.topview.context import TopViewContext
from town.topview.stage import Stage as TopViewArea
from cores.knight import KnightCore

class TownContext(Context):
  def __init__(ctx, party=[]):
    super().__init__()
    ctx.party = party or [KnightCore()]
    ctx.area = CentralArea
    ctx.graph = TownGraph(
      nodes=[CentralArea, FortuneArea, StoreArea],
      edges=[
        (CentralArea.links["door_triangle"], StoreArea.links["entrance"]),
        (CentralArea.links["door_heart"], FortuneArea.links["entrance"]),
      ]
    )

  def init(ctx):
    edge_link = ctx.graph.edges[0][0]
    area_link = ctx.area.links["door_triangle"]
    ctx.load_area(ctx.area)

  def load_area(ctx, area, link=None):
    if issubclass(area, SideViewArea):
      child = SideViewContext(area, ctx.graph, ctx.party, link)
    elif issubclass(area, TopViewArea):
      child = TopViewContext(area, ctx.party, link)
    ctx.open(child)
