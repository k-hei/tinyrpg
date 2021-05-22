from dungeon.actors import DungeonActor
from assets import load as use_assets
from anims.move import MoveAnim
from anims.jump import JumpAnim
from anims.attack import AttackAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
import pygame

class Mage(DungeonActor):
  def __init__(mage, core):
    super().__init__(core)

  def render(mage, anims):
    sprites = use_assets().sprites
    anim_group = [a for a in anims[0] if a.target is mage] if anims else []
    for anim in anim_group:
      if type(anim) is MoveAnim:
        if mage.facing == (0, -1):
          sprite = [
            sprites["mage_up"],
            sprites["mage_walkup0"],
            sprites["mage_up"],
            sprites["mage_walkup1"]
          ][anim.time % anim.duration // (anim.duration // 4)]
          break
        elif mage.facing == (0, 1):
          sprite = [
            sprites["mage_down"],
            sprites["mage_walkdown0"],
            sprites["mage_down"],
            sprites["mage_walkdown1"]
          ][anim.time % anim.duration // (anim.duration // 4)]
          break
        elif anim.time % (anim.duration // 2) >= anim.duration // 4:
          sprite = sprites["mage_walk"]
          break
      elif type(anim) is JumpAnim:
        if mage.facing == (0, -1):
          sprite = sprites["mage_walkup"]
        elif mage.facing == (0, 1):
          sprite = sprites["mage_walkdown"]
        else:
          sprite = sprites["mage_walk"]
        break
      elif (type(anim) is AttackAnim
      and anim.time < anim.duration // 2):
        if mage.facing == (0, -1):
          sprite = sprites["mage_walkup"]
        elif mage.facing == (0, 1):
          sprite = sprites["mage_walkdown"]
        else:
          sprite = sprites["mage_walk"]
        break
      elif type(anim) in (FlinchAnim, FlickerAnim):
        sprite = sprites["mage_flinch"]
        break
    else:
      if mage.facing == (0, -1):
        sprite = sprites["mage_up"]
      elif mage.facing == (0, 1):
        sprite = sprites["mage_down"]
      else:
        sprite = sprites["mage"]
    return super().render(sprite, anims)
