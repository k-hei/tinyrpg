from town.areas import Area
from town.actors.roguenpc import RogueNpc
from cores.rogue import RogueCore
from assets import load as use_assets
from sprite import Sprite
from config import ROGUE_NAME
from contexts.prompt import PromptContext, Choice

class OutskirtsArea(Area):
  bg_id = "town_outskirts"
  TOWER_X = 224

  def init(area, town):
    super().init(town)
    if (not town.ally
    or type(town.hero.core) is not RogueCore and type(town.ally.core) is not RogueCore):
      rogue = RogueNpc(name=ROGUE_NAME, messages=[
        lambda town: (
          (ROGUE_NAME, "Yeah, baby!"),
          PromptContext(("I'm gettin' hard!\nSo hard for you, baby!"), (
            Choice("\"So true\""),
            Choice("\"What?\"")
          ), required=True, on_close=lambda choice: (
            choice.text == "\"So true\"" and (
              (town.hero.core.name, "So true, bestie"),
              (ROGUE_NAME, "Oh baby, yes!"),
              (ROGUE_NAME, "Let's dance 'til the break of dawn!"),
              lambda: town.recruit(town.talkee)
            ) or choice.text == "\"What?\"" and (
              (town.hero.core.name, "What the hell are you talking about?"),
              (town.ally
                and (town.ally.core.name, "Let's just leave him be...")
                or (ROGUE_NAME, "You're no fun, you know that?"))
            )
          ))
        )
      ])
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
