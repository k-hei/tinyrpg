from cores.biped import BipedCore, SpriteMap
from config import MAGE_NAME, MAGE_HP
from contexts.prompt import PromptContext, Choice

class Mage(BipedCore):
  sprites = SpriteMap(
    face_right="mage",
    face_down="mage_down",
    face_up="mage_up",
    walk_right=("mage_walk", "mage", "mage_walk", "mage"),
    walk_down=("mage_walkdown0", "mage_down", "mage_walkdown1", "mage_down"),
    walk_up=("mage_walkup0", "mage_up", "mage_walkup1", "mage_up")
  )

  def __init__(mage, name=MAGE_NAME, faction="player", *args, **kwargs):
    super().__init__(
      name=name,
      faction=faction,
      hp=MAGE_HP,
      st=14,
      en=7,
      message=lambda ctx: [
        PromptContext((name.upper(), ": ", "Are you ready yet?"), (
          Choice("\"Let's go!\""),
          Choice("\"Maybe later...\"")
        ), required=True, on_close=lambda choice: (
          choice.text == "\"Let's go!\"" and (
            (ctx.hero.get_name(), "Let's get going!"),
            (name, "Jeez, about time..."),
            lambda: ctx.recruit(ctx.talkee)
          ) or choice.text == "\"Maybe later...\"" and (
            (ctx.hero.get_name(), "Give me a second..."),
            (name, "You know I don't have all day, right?")
          )
        ))
      ],
      *args,
      **kwargs
    )
