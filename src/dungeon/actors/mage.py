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
from skills.magic.accerso import Accerso
from skills.weapon.broadsword import BroadSword

class Mage(DungeonActor):
  drops = [BroadSword]

  def __init__(mage, core=None, *args, **kwargs):
    super().__init__(core=core or MageCore(skills=[Glacio, Accerso], *args, **kwargs))

  def step(mage, game):
    enemy = game.find_closest_enemy(mage)
    if enemy is None:
      return False

    skill = next((s for s in mage.core.skills if s.atk and enemy.cell in find_skill_targets(s, mage, game.floor)), None)
    if skill:
      return game.use_skill(mage, skill)

    skill = next((s for s in mage.core.skills if (
      not s.atk
      and not (s is Accerso and [e for e in [game.floor.get_elem_at(c, superclass=DungeonActor) for c in game.room.get_cells()] if (
        e and e is not mage
        and e.get_faction() == mage.get_faction()
      )])
    )), None)
    if skill:
      return game.use_skill(mage, skill)

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
