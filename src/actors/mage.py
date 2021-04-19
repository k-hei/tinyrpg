from assets import load as use_assets
from actors import Actor
from anims.move import MoveAnim
from anims.attack import AttackAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim

class Mage(Actor):
  def __init__(mage, skills):
    super().__init__(
      name="Mage",
      faction="player",
      hp=17,
      st=14,
      en=7,
      skills=skills
    )

  def render(mage, anims):
    sprites = use_assets().sprites
    anim_group = [a for a in anims[0] if a.target is mage] if anims else []
    for anim in anim_group:
      if (type(anim) is MoveAnim
      and anim.time % (anim.duration // 2) >= anim.duration // 4):
        sprite = sprites["mage_walk"]
        break
      elif (type(anim) is AttackAnim
      and anim.time < anim.duration // 2):
        sprite = sprites["mage_walk"]
        break
      elif type(anim) in (FlinchAnim, FlickerAnim):
        sprite = sprites["mage_flinch"]
        break
    else:
      sprite = sprites["mage"]
    return super().render(sprite, anims)
