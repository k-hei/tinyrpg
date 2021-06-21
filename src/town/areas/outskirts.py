from town.areas import Area, AreaLink
from town.actors.rogue import Rogue
from cores.rogue import Rogue
from assets import load as use_assets
from sprite import Sprite
from config import ROGUE_NAME
from contexts.prompt import PromptContext, Choice

class OutskirtsArea(Area):
  bg_id = "town_outskirts"
  TOWER_X = 224
  links = {
    "left": AreaLink(x=0, direction=(-1, 0)),
  }

  def init(area, town):
    super().init(town)
    if (not town.ally
    or type(town.hero.core) is not Rogue and type(town.ally.core) is not Rogue):
      rogue = Rogue()
      rogue.x = 144
      rogue.facing = (1, 0)
      area.actors.append(rogue)

  def render(area, hero, can_mark=True):
    assets = use_assets()
    sprite_bg = assets.sprites["town_outskirts"]
    sprite_tower = assets.sprites["tower"]
    nodes = super().render(hero, can_mark)
    nodes.append(Sprite(
      image=sprite_tower,
      pos=(OutskirtsArea.TOWER_X, Area.ACTOR_Y - 16)
    ))
    return nodes
