from town.sideview.stage import Area, AreaPort
from town.sideview.actor import Actor
from cores.mage import Mage

class CentralArea(Area):
  name = "Town Square"
  bg = "town_central"
  ports = {
    "right": AreaPort(x=416, direction=(1, 0)),
    "alley": AreaPort(x=272, direction=(0, -1)),
    "door_triangle": AreaPort(x=64, direction=(0, -1)),
    "door_heart": AreaPort(x=192, direction=(0, -1)),
  }

  def init(area, ctx):
    super().init(ctx)
    if ("minxia" in ctx.store.story
    and not next((c for c in ctx.store.party if type(c) is Mage), None)):
      area.spawn(Actor(core=Mage(
        faction="ally",
        facing=(1, 0)
      )), x=112)
