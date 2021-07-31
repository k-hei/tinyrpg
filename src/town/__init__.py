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
  def __init__(ctx, party=[Knight()], returning=False):
    super().__init__()
    ctx.party = party
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
    for char in ctx.party:
      char.anims.clear()
    if area is DungeonContext:
      return ctx.parent.goto_dungeon()
    if issubclass(area, SideViewArea):
      child = SideViewContext(area, ctx.graph, ctx.party, link)
    elif issubclass(area, TopViewArea):
      child = TopViewContext(area, ctx.party, link)
    ctx.open(child)

  def recruit(ctx, char):
    ctx.parent.recruit(char)
    if len(ctx.party) == 1:
      ctx.party.append(char)
    else:
      ctx.party[1] = char

  def get_inventory(ctx):
    return ctx.parent.get_inventory()
