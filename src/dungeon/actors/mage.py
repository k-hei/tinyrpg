import pygame
from dungeon.actors import DungeonActor
from cores.mage import Mage as MageCore
from assets import load as use_assets
from anims.move import MoveAnim
from anims.jump import JumpAnim
from anims.attack import AttackAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from sprite import Sprite
from skills import find_skill_targets
from skills.magic.glacio import Glacio

class Mage(DungeonActor):
  def __init__(mage, core=None, *args, **kwargs):
    super().__init__(core=core or MageCore(skills=[Glacio], *args, **kwargs))

  def step(mage, game):
    enemy = game.find_closest_enemy(mage)
    if enemy is None:
      return False
    for skill in mage.core.skills:
      target_cells = find_skill_targets(skill, mage, game.floor)
      if enemy.cell in target_cells:
        break
    else:
      return False
    if skill:
      game.use_skill(mage, skill)

  def view(mage, anims):
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
    return super().view(sprite, anims)
