from town.sideview.stage import Area, AreaLink
from town.sideview.actor import Actor
from cores.mage import Mage

class CentralArea(Area):
  name = "Town Square"
  bg = "town_central"
  links = {
    "right": AreaLink(x=416, direction=(1, 0)),
    "alley": AreaLink(x=272, direction=(0, -1)),
    "door_triangle": AreaLink(x=64, direction=(0, -1)),
    "door_heart": AreaLink(x=192, direction=(0, -1)),
  }

  def init(area, ctx):
    super().init(ctx)
    if ("minxia" in ctx.store.story
    and not next((c for c in ctx.store.party if type(c) is Mage), None)):
      area.spawn(Actor(core=Mage(
        faction="ally",
        facing=(1, 0)
      )), x=112)
