from actors import Actor
from assets import load as use_assets
from anims.move import MoveAnim
from anims.attack import AttackAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim

class Knight(Actor):
  def __init__(knight, skills):
    super().__init__(
      name="Knight",
      faction="player",
      hp=34,
      st=33,
      en=12,
      skills=skills
    )

  def render(knight, anims):
    sprites = use_assets().sprites
    anim_group = [a for a in anims[0] if a.target is knight] if anims else []
    for anim in anim_group:
      if type(anim) is MoveAnim:
        if anim.time % (anim.duration // 2) >= anim.duration // 4:
          sprite = sprites["knight_walk"]
          break
      elif type(anim) is AttackAnim:
        if anim.time < anim.duration // 2:
          sprite = sprites["knight_walk"]
          break
      elif type(anim) in (FlinchAnim, FlickerAnim):
        sprite = sprites["knight_flinch"]
        break
    else:
      sprite = sprites["knight"]
    return super().render(sprite, anims)
