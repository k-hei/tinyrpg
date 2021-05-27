from town.areas import Area, AreaLink
from town.actors.genie import Genie
from town.actors.mage import Mage
from cores.mage import MageCore

from assets import load as use_assets
from config import TILE_SIZE, WINDOW_WIDTH
from sprite import Sprite

from contexts.prompt import PromptContext, Choice
from contexts.nameentry import NameEntryContext
from contexts.load import LoadContext
from contexts.save import SaveContext

class CentralArea(Area):
  bg_id = "town_central"

  def init(area, town):
    super().init(town)
    prompt = lambda: PromptContext("How fares the exploration?", (
      Choice("Manage data", closing=True),
      Choice("Change name"),
      Choice("Nothing", closing=True)
    ), required=True, on_close=lambda choice: (
      choice.text == "Manage data" and [
        lambda: PromptContext("What would you like to do?", (
          Choice("Load data"),
          Choice("Save data"),
          Choice("Nothing", closing=True)
        ), required=True, on_close=lambda choice: (
          choice.text == "Load data" and [
            lambda: LoadContext(
              on_close=lambda data: (
                data and town.parent.load(data)
                or [prompt]
              )
            )
          ] or choice.text == "Save data" and [
            lambda: SaveContext(
              data=town.parent.save(),
              on_close=lambda _: [prompt]
            )
           ] or choice.text == "Nothing" and [prompt]
        ))
      ] or choice.text == "Change name" and [
        ("Doshin", "Hm? A name change?"),
        ("Doshin", "Awfully finnicky, aren't we?"),
        lambda: NameEntryContext(
          char=town.hero.core,
          on_close=lambda name: (
            name != town.hero.core.name and (
              town.hero.core.rename(name),
              ("Doshin", lambda: ("Oho! So your name is ", town.hero.core.token(), ".")),
              ("Doshin", ". . . . ."),
              ("Doshin", "...Well, it's certainly something.")
            ) or (
              ("Doshin", "Oh, changed your mind?"),
              ("Doshin", "Well, if we ever figure out our little identity crisis, you know where to find me.")
            )
          )
        )
      ] or choice.text == "Nothing" and []
    ))
    genie = Genie(name="Doshin", messages=[
      lambda town: [
        ("Doshin", "Hail, traveler!"),
        prompt
      ]
    ])
    genie.x = 32
    genie.facing = (1, 0)
    area.actors.append(genie)

    if (not town.ally
    or type(town.hero.core) is not MageCore and type(town.ally.core) is not MageCore):
      mage = Mage()
      mage.x = 304
      mage.facing = (1, 0)
      area.actors.append(mage)

    area.links = [
      AreaLink(x=272, direction=(0, -1), target_area="ClearingArea", target_x=96),
      AreaLink(x=192, direction=(0, -1), target_area="ClearingArea", target_x=96)
    ]

  def render(area, hero, can_mark=True):
    nodes = super().render(hero, can_mark)
    for i, sprite in enumerate(nodes):
      if i == 0:
        continue
      x, y = sprite.pos
      sprite.pos = (x, y - TILE_SIZE // 4)
    return nodes
