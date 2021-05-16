from town.areas import Area
from town.actors.genie import Genie

from assets import load as use_assets
from config import TILE_SIZE
from sprite import Sprite

from contexts.nameentry import NameEntryContext

class CentralArea(Area):
  def __init__(area, town):
    genie = Genie(name="Doshin", messages=(
      (
        ("Doshin", "Hail, traveler!"),
        ("Doshin", "How fares the exploration?")
      ),
      (
        ("Doshin", "Hm? A name change?"),
        ("Doshin", "Awfully finnicky, aren't we?"),
        NameEntryContext(default_name=town.hero.core.name, on_close=lambda name: (
          town.hero.core.rename(name)
        )),
        ("Doshin", lambda: (
          "Oho! So your name is ", town.hero.core.token(), "."
        )),
        ("Doshin", "...Well, it's something.")
      )
    ))
    genie.x = 112
    genie.facing = 1
    area.actors = [genie]

  def render(area, hero):
    nodes = super().render(hero)
    for i, sprite in enumerate(nodes):
      x, y = sprite.pos
      sprite.pos = (x, y - TILE_SIZE // 4)
    assets = use_assets()
    sprite_bg = assets.sprites["town_central"]
    nodes.insert(0, Sprite(
      image=sprite_bg,
      pos=(0, 0)
    ))
    return nodes
