from town.sideview.stage import Area, AreaLink
from town.sideview.actor import Actor
from cores.genie import Genie
from cores.mage import Mage as Mage

from assets import load as use_assets
from config import TILE_SIZE, WINDOW_WIDTH
from sprite import Sprite

from contexts.prompt import PromptContext, Choice
from contexts.nameentry import NameEntryContext
from contexts.load import LoadContext
from contexts.save import SaveContext

class CentralArea(Area):
  name = "Town Square"
  bg = "town_central"
  links = {
    "right": AreaLink(x=416, direction=(1, 0)),
    "alley": AreaLink(x=272, direction=(0, -1)),
    "door_triangle": AreaLink(x=64, direction=(0, -1)),
    "door_heart": AreaLink(x=192, direction=(0, -1)),
  }

  def init(area, ctx):
    super().init(ctx)

    area.spawn(Actor(core=Genie(
      name="Doshin",
      facing=(1, 0),
      message=lambda ctx: [
        ("Doshin", "Hail, traveler!"),
        prompt := lambda: PromptContext("How fares the exploration?", (
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
                    data and ctx.parent.load(data)
                    or [prompt]
                  )
                )
              ] or choice.text == "Save data" and [
                lambda: SaveContext(
                  data=ctx.parent.save(),
                  on_close=lambda _: [prompt]
                )
              ] or choice.text == "Nothing" and [prompt]
            ))
          ] or choice.text == "Change name" and [
            ("Doshin", "Hm? A name change?"),
            ("Doshin", "Awfully finnicky, aren't we?"),
            lambda: NameEntryContext(
              char=ctx.hero.core,
              on_close=lambda name: (
                name != ctx.hero.core.name and (
                  ctx.hero.core.rename(name),
                  ("Doshin", lambda: ("Oho! So your name is ", ctx.hero.core.token(), ".")),
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
    )), (32, 0))

    area.spawn(Actor(core=Mage(
      faction="ally",
      facing=(1, 0)
    )), (304, 0))
