from town.areas import Area
from assets import load as use_assets
from sprite import Sprite

class OutskirtsArea(Area):
  TOWER_X = 224

  def __init__(area):
    super().__init__()

  def render(area, hero):
    assets = use_assets()
    sprite_bg = assets.sprites["town_outskirts"]
    sprite_tower = assets.sprites["tower"]
    nodes = super().render(hero)
    nodes.insert(0, Sprite(
      image=sprite_bg,
      pos=(0, 0)
    ))
    nodes.append(Sprite(
      image=sprite_tower,
      pos=(OutskirtsArea.TOWER_X, Area.ACTOR_Y - 16)
    ))
    return nodes
