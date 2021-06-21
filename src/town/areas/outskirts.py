from town.sideview.stage import Area, AreaLink
from assets import load as use_assets
from sprite import Sprite
from config import ROGUE_NAME
from contexts.prompt import PromptContext, Choice

class OutskirtsArea(Area):
  name = "Outskirts"
  TOWER_X = 224
  bg = "town_outskirts"
  links = {
    "left": AreaLink(x=0, direction=(-1, 0)),
  }

  def view(area, hero, link):
    sprites = super().view(hero, link)
    assets = use_assets()
    sprite_bg = assets.sprites["town_outskirts"]
    sprite_tower = assets.sprites["tower"]
    sprites.append(Sprite(
      image=sprite_tower,
      pos=(OutskirtsArea.TOWER_X, Area.ACTOR_Y - 32)
    ))
    return sprites
