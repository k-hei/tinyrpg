from town.sideview.stage import Area, AreaLink
from town.sideview.actor import Actor
from cores.rat import Rat
from config import TILE_SIZE

class ClearingArea(Area):
  name = "Alleyway"
  bg = "town_clearing"
  links = {
    "alley": AreaLink(x=96, direction=(0, 1)),
  }

  def init(area, town):
    super().init(town)
    area.spawn(Actor(core=Rat(
      name=(rat_name := "Rascal"),
      message=lambda town: [
        (rat_name, "Fuck you")
      ])
    ), (160, 0))
