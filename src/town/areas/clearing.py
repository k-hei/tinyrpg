from town.areas import Area, AreaLink
from town.actors.rat import Rat
from config import TILE_SIZE

class ClearingArea(Area):
  bg_id = "town_clearing"
  links = {
    "alley": AreaLink(x=96, direction=(0, 1)),
  }

  def init(area, town):
    super().init(town)
    rat = Rat(name="Rascal", messages=[
      lambda town: [(rat.get_name(), "Fuck you")],
      lambda town: [(rat.get_name(), "Whore")]
    ])
    rat.x = 160
    area.actors.append(rat)

  def render(area, hero, can_mark=True):
    nodes = super().render(hero, can_mark)
    for i, sprite in enumerate(nodes):
      if i == 0:
        continue
      x, y = sprite.pos
      sprite.pos = (x, y - TILE_SIZE // 4)
    return nodes
