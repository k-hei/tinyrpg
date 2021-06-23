from dungeon.actors import DungeonActor
from cores import Core
from assets import load as use_assets
from skills.weapon.tackle import Tackle
from anims.move import MoveAnim
from anims.attack import AttackAnim
from anims.awaken import AwakenAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from items.materials.angeltears import AngelTears
from sprite import Sprite

class Eye(DungeonActor):
  drops = [AngelTears]

  def __init__(eye):
    super().__init__(Core(
      name="Eyeball",
      faction="enemy",
      hp=20,
      st=12,
      en=7,
      skills=[ Tackle ]
    ))

  def render(eye, anims):
    sprites = use_assets().sprites
    sprite = None
    for anim_group in anims:
      for anim in [a for a in anim_group if a.target is eye]:
        if type(anim) is AwakenAnim:
          return super().render(sprites["eye_attack"], anims)
    if eye.is_dead():
      return super().render(sprites["eye_flinch"], anims)
    anim_group = [a for a in anims[0] if a.target is eye] if anims else []
    for anim in anim_group:
      if type(anim) is MoveAnim:
        sprite = sprites["eye_attack"]
        break
      elif (type(anim) is AttackAnim
      and anim.time < anim.duration // 2):
        sprite = sprites["eye_attack"]
        break
      elif type(anim) in (FlinchAnim, FlickerAnim):
        sprite = sprites["eye_flinch"]
        break
    else:
      if eye.ailment == "sleep":
        sprite = sprites["eye_attack"]
      else:
        sprite = sprites["eye"]
    return super().render([Sprite(image=sprite)], anims)
