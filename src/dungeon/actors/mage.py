import lib.vector as vector
from dungeon.actors import DungeonActor
from cores.mage import Mage as MageCore
from helpers.mage import step_move
from skills.weapon.cudgel import Cudgel
from skills.magic.glacio import Glacio
from skills.magic.congelatio import Congelatio
from skills.weapon.broadsword import BroadSword

import assets
from anims.step import StepAnim
from anims.path import PathAnim
from anims.jump import JumpAnim
from anims.attack import AttackAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from anims.shake import ShakeAnim
from anims.drop import DropAnim
from anims.fall import FallAnim
from anims.walk import WalkAnim

class Mage(DungeonActor):
  drops = [BroadSword]

  def __init__(mage, core=None, faction="ally", ailment=None, ailment_turns=0, *args, **kwargs):
    super().__init__(
      core=core or MageCore(faction=faction, skills=[Cudgel], *args, **kwargs),
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

    if faction == "enemy":
      mage.hp_max *= 6
      mage.hp = mage.hp_max
    else:
      mage.hp_max = mage.core.get_hp_max()

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

  def start_move(actor, running):
    actor.anims = [WalkAnim(period=30 if running else 60)]
    actor.core.anims = actor.anims.copy()

  def stop_move(actor):
    actor.anims = []
    actor.core.anims = []

  def animate_brandish(mage, delay=0, on_end=None):
    return [
      JumpAnim(
        target=mage,
        height=28,
        delay=mage.core.BrandishAnim.frames_duration[0] + delay,
        duration=mage.core.BrandishAnim.jump_duration,
      ),
      mage.core.BrandishAnim(
        target=mage,
        delay=delay,
        on_end=lambda: (
          mage.stop_move(),
          mage.core.anims.insert(0, mage.core.IdleDownAnim()),
          on_end and on_end(),
        )
      )
    ]

  def wake_up(mage):
    if not super().wake_up():
      return False  # not sleeping

    if not mage.weapon:
      return True

    mage.core.anims += mage.animate_brandish()
    return True

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
      if mage.hp < mage.hp_max / 2:
        mage.charge(skill=Congelatio, dest=enemy.cell)
        game.comps.minilog.print((mage.token(), " is chanting."))
      elif not next((e for e in game.stage.get_elems_at(vector.add(mage.cell, mage.facing)) if e.solid), None):
        mage.charge(skill=Glacio)
        game.comps.minilog.print((mage.token(), " is chanting."))

    has_allies = next((e for c in game.room.get_cells() for e in game.stage.get_elems_at(c) if (
      e
      and e is not mage
      and isinstance(e, DungeonActor)
      and e.faction == mage.faction
    )), None)

    if not has_allies:
      mage.charge(skill="Roulette", turns=1)
      return game.comps.minilog.print((mage.token(), " is chanting."))

    return step_move(mage, game)

  def view(mage, anims):
    sprites = assets.sprites

    anim_group = [a for a in anims[0] if a.target is mage] if anims else []
    anim_group += mage.core.anims

    will_fall = anims and next((a for a in anims[0] if type(a) is FallAnim), None)
    if will_fall and anims[0].index(will_fall) > 0:
      return DungeonActor.view(mage, sprites["mage_shock"], anims)

    for anim in anim_group:
      if type(anim) is LeapAnim:
        sprite = sprites["mage_leap"]
        break
      elif type(anim) is StepAnim or isinstance(anim, (PathAnim, WalkAnim)):
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

    # reused in MageClone
    return DungeonActor.view(mage, sprite, anims)

class LeapAnim(JumpAnim): pass
