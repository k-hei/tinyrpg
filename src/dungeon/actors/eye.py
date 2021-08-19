from random import randint, choice
from lib.cell import is_adjacent
from dungeon.actors import DungeonActor
from cores import Core, Stats
from assets import sprites
from skills.weapon.tackle import Tackle
from skills.ailment.steal import Steal
from skills.armor.hpup import HpUp
from anims.move import MoveAnim
from anims.attack import AttackAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from anims.awaken import AwakenAnim
from items.materials.angeltears import AngelTears
from sprite import Sprite
from filters import replace_color
from colors.palette import BLACK, CYAN
from config import PUSH_DURATION

def IdleSprite(facing):
  if facing == (0, 1):
    return sprites["eyeball"]
  elif facing == (0, -1):
    return sprites["eyeball_up"]
  elif facing[0]:
    return sprites["eyeball_right"]

def MoveSprite(facing):
  if facing == (0, 1):
    return sprites["eyeball_move"]
  elif facing == (0, -1):
    return sprites["eyeball_move_up"]
  elif facing[0]:
    return sprites["eyeball_move_right"]

def FlinchSprite(facing):
  if facing == (0, 1):
    return sprites["eyeball_flinch"]
  elif facing == (0, -1):
    return sprites["eyeball_flinch_up"]
  elif facing[0]:
    return sprites["eyeball_flinch_right"]

def SleepSprite(facing):
  if facing == (0, 1):
    return sprites["eyeball_sleep"]
  elif facing == (0, -1):
    return sprites["eyeball_sleep_up"]
  elif facing[0]:
    return sprites["eyeball_sleep_right"]

class Eyeball(DungeonActor):
  drops = [AngelTears]
  skill = HpUp

  def __init__(eye, faction="enemy", rare=False,  *args, **kwargs):
    super().__init__(Core(
      name="Eyeball",
      faction=faction,
      stats=Stats(
        hp=14,
        st=12,
        dx=5,
        ag=6,
        lu=3,
        en=11,
      ),
      skills=[Tackle]
    ), *args, **kwargs)
    eye.item = None
    if rare:
      eye.promote(hp=False)
      eye.core.skills.append(HpUp)

  def view(eyeball, anims):
    sprite = None
    for anim_group in anims:
      for anim in [a for a in anim_group if a.target is eyeball]:
        if type(anim) is AwakenAnim:
          return super().view(MoveSprite(eyeball.facing), anims)
    if eyeball.is_dead():
      return super().view(FlinchSprite(eyeball.facing), anims)
    anim_group = [a for a in anims[0] if a.target is eyeball] if anims else []
    for anim in anim_group:
      if type(anim) is MoveAnim and anim.duration != PUSH_DURATION:
        sprite = MoveSprite(eyeball.facing)
        break
      elif (type(anim) is AttackAnim
      and anim.time >= 0
      and anim.time < anim.duration // 2):
        sprite = MoveSprite(eyeball.facing)
        break
      elif type(anim) in (FlinchAnim, FlickerAnim):
        sprite = FlinchSprite(eyeball.facing)
        break
    else:
      if eyeball.ailment == "sleep":
        sprite = SleepSprite(eyeball.facing)
      else:
        sprite = IdleSprite(eyeball.facing)
    if eyeball.ailment == "freeze":
      sprite = FlinchSprite(eyeball.facing)
    return super().view(sprite, anims)
