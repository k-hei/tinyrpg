from actors import Actor
from assets import load as use_assets
from anims.move import MoveAnim
from anims.attack import AttackAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
import pygame

class Knight(Actor):
  def __init__(knight, skills=[]):
    super().__init__(
      name="Knight",
      faction="player",
      hp=23,
      st=17,
      en=9,
      skills=skills
    )

  def render(knight, anims):
    sprites = use_assets().sprites
    anim_group = [a for a in anims[0] if a.target is knight] if anims else []
    for anim in anim_group:
      if type(anim) is MoveAnim:
        if knight.facing == (0, 1):
          sprite = sprites["knight_down"]
          if anim.time % (anim.duration // 2) >= anim.duration // 4:
            sprite = sprites["knight_walkdown"]
          if anim.time % anim.duration >= anim.duration // 2:
            sprite = pygame.transform.flip(sprite, True, False)
          break
        elif anim.time % (anim.duration // 2) >= anim.duration // 4:
          sprite = sprites["knight_walk"]
          break
      elif type(anim) is AttackAnim and anim.time < anim.duration // 2:
        if knight.facing == (0, 1):
          sprite = sprites["knight_down"]
        else:
          sprite = sprites["knight"]
        break
      elif type(anim) in (FlinchAnim, FlickerAnim):
        sprite = sprites["knight_flinch"]
        break
    else:
      if knight.facing == (0, 1):
        sprite = sprites["knight_down"]
      else:
        sprite = sprites["knight"]
    return super().render(sprite, anims)
