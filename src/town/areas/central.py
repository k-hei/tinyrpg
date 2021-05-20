from town.areas import Area
from town.actors.genie import Genie
from town.actors.magenpc import MageNpc
from cores.mage import MageCore

from assets import load as use_assets
from config import TILE_SIZE
from sprite import Sprite

from contexts.nameentry import NameEntryContext
from contexts.prompt import PromptContext, Choice

class CentralArea(Area):
  def __init__(area):
    super().__init__()

  def init(area, town):
    genie = Genie(name="Doshin", messages=[
      lambda town: [
        ("Doshin", "Hail, traveler!"),
        PromptContext("How fares the exploration?", (
          Choice("Load data"),
          Choice("Save data"),
          Choice("Change name"),
          Choice("Nothing")
        ), required=True, on_close=lambda choice: (
          choice.text == "Load data" and [
            (None, "Save data loaded successfully."),
            lambda: town.parent.dissolve(on_clear=town.parent.load)
          ] or choice.text == "Save data" and [
            ("Doshin", "Sorry, we're still working on this feature!")
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
      ]
    ])
    genie.x = 32
    genie.facing = 1
    area.actors.append(genie)

    if (not town.ally
    or type(town.hero.core) is not MageCore and type(town.ally.core) is not MageCore):
      mage = MageNpc(messages=[
        lambda town: [
          PromptContext((mage.get_name().upper(), ": ", "Are you ready yet?"), (
            Choice("\"Let's go!\""),
            Choice("\"Not yet...\"")
          ), on_close=lambda choice: (
            choice.text == "\"Let's go!\"" and (
              (town.hero.get_name(), "Let's get going!"),
              (mage.get_name(), "Jeez, about time..."),
              lambda: town.recruit(town.talkee)
            ) or choice.text == "\"Not yet...\"" and (
              (town.hero.get_name(), "Give me a second..."),
              (mage.get_name(), "You know I don't have all day, right?")
            )
          ))
        ]
      ])
      mage.x = 112
      mage.facing = 1
      area.actors.append(mage)

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
