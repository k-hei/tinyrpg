from town.sideview.stage import Area, AreaLink
from town.sideview.actor import Actor
from cores.genie import Genie
from assets import load as use_assets
from sprite import Sprite
from config import TILE_SIZE
from contexts.prompt import PromptContext, Choice
from contexts.load import LoadContext
from contexts.save import SaveContext
from contexts.nameentry import NameEntryContext

class OutskirtsArea(Area):
  name = "Outskirts"
  TOWER_X = 224
  bg = "town_outskirts"
  links = {
    "left": AreaLink(x=0, direction=(-1, 0)),
    "tower": AreaLink(x=TOWER_X, direction=(1, 0)),
  }

  def init(area, ctx):
    super().init(ctx)
    area.spawn(Actor(core=Genie(
      name="Doshin",
      facing=(-1, 0),
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
                    data and ctx.get_root().child.load(data)
                    or [prompt]
                  )
                )
              ] or choice.text == "Save data" and [
                lambda: SaveContext(
                  data=ctx.get_root().child.save(),
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
    )), x=144)

  def view(area, hero, link):
    sprites = super().view(hero, link)
    assets = use_assets()
    sprite_bg = assets.sprites["town_outskirts"]
    sprite_tower = assets.sprites["tower"]
    sprites.append(Sprite(
      image=sprite_tower,
      pos=(OutskirtsArea.TOWER_X, Area.ACTOR_Y - TILE_SIZE)
    ))
    return sprites
