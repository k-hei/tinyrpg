from town.areas import Area
from town.actors.rogue import Rogue
from assets import load as use_assets
from sprite import Sprite
from config import ROGUE_NAME

class OutskirtsArea(Area):
  TOWER_X = 224

  def __init__(area):
    super().__init__()
    rogue = Rogue(name=ROGUE_NAME, messages=[
      lambda town: (
        (ROGUE_NAME, "Yeah, baby!"),
        (ROGUE_NAME, "I'm gettin' hard!"),
        (ROGUE_NAME, "So hard for you, baby!"),
        (None, ". . . . ."),
        (town.ally.core.name, "Let's just leave him be...")
      )
    ])
    rogue.x = 144
    rogue.facing = 1
    area.actors = [rogue]

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
