from random import randint, choice
import pygame
from dungeon.actors import DungeonActor
from cores.mage import Mage as MageCore
from assets import load as use_assets
from anims.move import MoveAnim
from anims.path import PathAnim
from anims.jump import JumpAnim
from anims.attack import AttackAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from anims.shake import ShakeAnim
from anims.drop import DropAnim
from anims.frame import FrameAnim
from anims.fall import FallAnim
from anims.pause import PauseAnim
from lib.sprite import Sprite
from skills.magic.glacio import Glacio
from skills.magic.congelatio import Congelatio
from skills.magic.accerso import Accerso
from skills.weapon.broadsword import BroadSword

class Mage(DungeonActor):
  drops = [BroadSword]

  def __init__(mage, core=None, faction="ally", ailment=None, ailment_turns=0, *args, **kwargs):
    super().__init__(
      core=core or MageCore(faction=faction, skills=[Glacio, Accerso], *args, **kwargs),
      ailment=ailment,
      ailment_turns=ailment_turns,
      aggro=3,
      behavior="guard" if faction == "ally" else "chase"
    )

  def encode(mage):
    [cell, kind, *props] = super().encode()
    return [cell, kind, {
      **(props[0] if props else {}),
      **(mage.charge_skill and { "charge_skill": mage.charge_skill } or {}),
      **(mage.charge_dest and { "charge_dest": mage.charge_dest } or {}),
      **(mage.charge_turns and { "charge_turns": mage.charge_turns } or {})
    }]

  @DungeonActor.faction.setter
  def faction(mage, faction):
    DungeonActor.faction.fset(mage, faction)
    if faction in ("player", "enemy"):
      mage.behavior = "chase"
    else:
      mage.behavior = "guard"

  def spawn(mage, stage, cell):
    super().spawn(stage, cell)
    mage.faction = mage.faction

  def charge(mage, *args, **kwargs):
    super().charge(*args, **kwargs)
    mage.core.anims.append(MageCore.CastAnim())

  def step(mage, game):
    if mage.behavior == "guard":
      return None

    enemy = game.find_closest_enemy(mage)
    if not mage.aggro:
      return super().step(game)
    if enemy is None:
      return None

    mage_x, mage_y = mage.cell
    enemy_x, enemy_y = enemy.cell
    dist_x = enemy_x - mage_x
    delta_x = dist_x // (abs(dist_x) or 1)
    dist_y = enemy_y - mage_y
    delta_y = dist_y // (abs(dist_y) or 1)

    mage.face(enemy.cell)
    if (delta_x == 0 and dist_y <= Glacio.range_max
    or delta_y == 0 and dist_x <= Glacio.range_max
    ) and not enemy.ailment == "freeze" and not abs(dist_x) + abs(dist_y) == 1:
      if mage.get_hp() < mage.get_hp_max() / 2:
        mage.charge(skill=Congelatio, dest=enemy.cell)
      else:
        mage.charge(skill=Glacio)
      return game.log.print((mage.token(), " is chanting."))

    has_allies = next((e for e in [game.floor.get_elem_at(c, superclass=DungeonActor) for c in game.room.get_cells()] if (
      e and e is not mage
      and e.faction == mage.faction
    )), None)

    if not has_allies:
      return ("use_skill", Accerso)

    delta = None
    if abs(dist_x) + abs(dist_y) == 1:
      if game.floor.is_cell_empty((mage_x - delta_x, mage_y - delta_y)):
        delta = (-delta_x, -delta_y)
      else:
        deltas = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        deltas = [(dx, dy) for (dx, dy) in deltas if game.floor.is_cell_empty((mage_x + dx, mage_y + dy))]
        if deltas:
          delta = choice(deltas)
    elif abs(dist_x) + abs(dist_y) < 4:
      if delta_x and delta_y:
        delta = randint(0, 1) and (-delta_x, 0) or (0, -delta_y)
      elif delta_x:
        delta = (-delta_x, 0)
      elif delta_y:
        delta = (0, -delta_y)
    else:
      if delta_x and delta_y:
        delta = randint(0, 1) and (delta_x, 0) or (0, delta_y)
      elif delta_x:
        delta = (delta_x, 0)
      elif delta_y:
        delta = (0, delta_y)
    if delta:
      return ("move", delta)

  def view(mage, anims):
    sprites = use_assets().sprites
    anim_group = [a for a in anims[0] if a.target is mage] if anims else []
    will_fall = anims and next((a for a in anims[0] if type(a) is FallAnim), None)
    if will_fall and anims[0].index(will_fall) > 0:
      return super().view(sprites["mage_shock"], anims)
    for anim in anim_group:
      if type(anim) is MoveAnim or type(anim) is PathAnim:
        x4_idx = max(0, int((anim.time - 1) % anim.period // (anim.period / 4)))
        if mage.facing == (0, -1):
          sprite = [
            sprites["mage_up"],
            sprites["mage_walkup0"],
            sprites["mage_up"],
            sprites["mage_walkup1"]
          ][x4_idx]
          break
        elif mage.facing == (0, 1):
          sprite = [
            sprites["mage_down"],
            sprites["mage_walkdown0"],
            sprites["mage_down"],
            sprites["mage_walkdown1"]
          ][x4_idx]
          break
        elif anim.time % (anim.period // 2) >= anim.period // 4:
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
      elif type(anim) in (FlinchAnim, FlickerAnim, DropAnim):
        sprite = sprites["mage_flinch"]
        break
      elif type(anim) is ShakeAnim:
        sprite = sprites["mage_shock"]
        break
      elif type(anim) is FallAnim:
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
