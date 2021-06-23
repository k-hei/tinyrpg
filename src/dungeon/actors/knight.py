import pygame
from dungeon.actors import DungeonActor
from assets import load as use_assets
from anims.move import MoveAnim
from anims.jump import JumpAnim
from anims.attack import AttackAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from sprite import Sprite

class Knight(DungeonActor):
  def __init__(knight, core):
    super().__init__(core)

  def view(knight, anims):
    assets = use_assets().sprites
    anim_group = [a for a in anims[0] if a.target is knight] if anims else []
    for anim in anim_group:
      if type(anim) is MoveAnim:
        if knight.facing == (0, -1):
          sprite = [
            assets["knight_up"],
            assets["knight_walkup0"],
            assets["knight_up"],
            assets["knight_walkup1"]
          ][anim.time % anim.duration // (anim.duration // 4)]
          break
        if knight.facing == (0, 1):
          sprite = [
            assets["knight_down"],
            assets["knight_walkdown0"],
            assets["knight_down"],
            assets["knight_walkdown1"]
          ][anim.time % anim.duration // (anim.duration // 4)]
          break
        elif anim.time % (anim.duration // 2) >= anim.duration // 4:
          sprite = assets["knight_walk"]
          break
      elif type(anim) is JumpAnim:
        if knight.facing == (0, -1):
          sprite = assets["knight_walkup"]
        elif knight.facing == (0, 1):
          sprite = assets["knight_walkdown"]
        else:
          sprite = assets["knight_walk"]
        break
      elif type(anim) is AttackAnim and anim.time < anim.duration // 2:
        if knight.facing == (0, -1):
          sprite = assets["knight_up"]
        elif knight.facing == (0, 1):
          sprite = assets["knight_down"]
        else:
          sprite = assets["knight"]
        break
      elif type(anim) in (FlinchAnim, FlickerAnim):
        sprite = assets["knight_flinch"]
        break
    else:
      if knight.facing == (0, -1):
        sprite = assets["knight_up"]
      elif knight.facing == (0, 1):
        sprite = assets["knight_down"]
      else:
        sprite = assets["knight"]
    return super().view([Sprite(image=sprite)], anims)
