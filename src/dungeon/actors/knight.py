import pygame
from dungeon.actors import DungeonActor
from cores.knight import Knight as KnightCore
from assets import load as use_assets
from anims.move import MoveAnim
from anims.jump import JumpAnim
from anims.attack import AttackAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from anims.shake import ShakeAnim
from anims.drop import DropAnim
from anims.path import PathAnim
from sprite import Sprite

class Knight(DungeonActor):
  def __init__(knight, core=None, *args, **kwargs):
    super().__init__(core=core or KnightCore(*args, **kwargs))

  def view(knight, anims):
    assets = use_assets().sprites
    anim_group = [a for a in anims[0] if a.target is knight] if anims else []
    for anim in anim_group:
      if type(anim) is MoveAnim or type(anim) is PathAnim:
        x4_idx = max(0, int((anim.time - 1) % anim.period // (anim.period / 4)))
        if knight.facing == (0, -1):
          sprite = [
            assets["knight_up"],
            assets["knight_walkup0"],
            assets["knight_up"],
            assets["knight_walkup1"]
          ][x4_idx]
          break
        if knight.facing == (0, 1):
          sprite = [
            assets["knight_down"],
            assets["knight_walkdown0"],
            assets["knight_down"],
            assets["knight_walkdown1"]
          ][x4_idx]
          break
        elif anim.time % (anim.period // 2) >= anim.period // 4:
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
      elif type(anim) in (FlinchAnim, FlickerAnim, ShakeAnim, DropAnim):
        sprite = assets["knight_flinch"]
        break
    else:
      if knight.facing == (0, -1):
        sprite = assets["knight_up"]
      elif knight.facing == (0, 1):
        sprite = assets["knight_down"]
      else:
        sprite = assets["knight"]
    if knight.ailment == "freeze":
      sprite = assets["knight_flinch"]
    return super().view(sprite, anims)
