from cores import Stats
from cores.biped import BipedCore, SpriteMap
from config import MAGE_NAME, MAGE_HP

from contexts.prompt import PromptContext, Choice
from contexts.dialogue import DialogueContext

from assets import assets
from anims.frame import FrameAnim

class Mage(BipedCore):
  sprites = SpriteMap(
    face_right="mage",
    face_down="mage_down",
    face_up="mage_up",
    walk_right=("mage_walk", "mage", "mage_walk", "mage"),
    walk_down=("mage_walkdown0", "mage_down", "mage_walkdown1", "mage_down"),
    walk_up=("mage_walkup0", "mage_up", "mage_walkup1", "mage_up")
  )

  class SleepAnim(FrameAnim):
    frames = assets.sprites["mage_sleep"]
    frames_duration = 30
    loop = True

  class ThinkAnim(FrameAnim):
    frames = [assets.sprites["mage_sleep"][0]]
    frames_duration = 1
    loop = True

  class CastAnim(FrameAnim):
    frames = assets.sprites["mage_cast"]
    frames_duration = 10
    loop = True

  class LaughAnim(FrameAnim):
    frames = assets.sprites["mage_sleep"][0:2]
    frames_duration = 8
    loop = True

  class CheekyAnim(FrameAnim):
    frames = assets.sprites["mage_cheeky"]
    frames_duration = 10
    loop = True

  class YellAnim(FrameAnim):
    frames = [assets.sprites["mage_yell"]]

  class BrandishAnim(FrameAnim):
    frames = assets.sprites["mage_brandish"]
    frames_duration = [10, 5, 5, 7, 9, 15]
    jump_duration = 26

  class IdleDownAnim(FrameAnim):
    frames = assets.sprites["mage_idle_down"]
    frames_duration = 10
    loop = True

  def __init__(mage, name=MAGE_NAME, faction="player", hp=MAGE_HP, *args, **kwargs):
    super().__init__(
      name=name,
      faction=faction,
      hp=hp,
      stats=Stats(
        hp=MAGE_HP,
        st=14,
        ma=14,
        dx=9,
        ag=7,
        lu=9,
        en=10,
      ),
      message=lambda ctx: DialogueContext(script=[
        (hero := ctx.party[0]) and None,
        PromptContext((name.upper(), ": ", "Are you ready yet?"), (
          Choice("\"Let's go!\""),
          Choice("\"Maybe later...\"")
        ), required=True, on_close=lambda choice: (
          choice.text == "\"Let's go!\"" and (
            (hero.name, "Let's get going!"),
            (name, "Jeez, about time..."),
            lambda: ctx.recruit(ctx.talkee)
          ) or choice.text == "\"Maybe later...\"" and (
            (hero.name, "Give me a second..."),
            (name, "You know I don't have all day, right?")
          )
        ))
      ]),
      *args,
      **kwargs
    )
