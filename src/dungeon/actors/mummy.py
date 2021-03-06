from random import random, randint
from dungeon.actors import DungeonActor
from cores import Core, Stats
from dungeon.stage import Tile
from helpers.stage import is_cell_walkable_to_actor
from skills.attack import AttackSkill
from skills.attack.clawrush import ClawRush
from skills.support import SupportSkill
from skills.weapon.club import Club
from lib.cell import is_adjacent, add as add_vector
from lib.compose import compose
from lib.direction import invert as invert_direction
from lib.sprite import Sprite
import assets
from anims.step import StepAnim
from anims.jump import JumpAnim
from anims.attack import AttackAnim
from anims.shake import ShakeAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from anims.pause import PauseAnim
from items.materials.crownjewel import CrownJewel
from vfx.linen import LinenVfx
from config import PUSH_DURATION

class Mummy(DungeonActor):
  drops = [CrownJewel]
  skill = ClawRush
  idle_messages = [
    "The {enemy} grunts nastily.",
    "The {enemy} stands eerily still.",
  ]

  class ChargeAnim(ShakeAnim): pass

  class LinenWhip(AttackSkill):
    name = "LinenWhip"
    charge_turns = 1

    def effect(game, user, dest, on_start=None, on_end=None):
      user_x, user_y = user.cell
      dest_x, dest_y = dest
      dist_x = dest_x - user_x
      dist_y = dest_y - user_y
      delta_x = dist_x // abs(dist_x or 1)
      delta_y = dist_y // abs(dist_y or 1)
      cell = (user_x + delta_x, user_y + delta_y)
      while (cell != dest
      and not (Tile.is_solid(game.stage.get_tile_at(cell)) and not game.stage.is_tile_at_pit(cell))
      and not next((e for e in game.stage.get_elems_at(cell) if e.solid), None)
      ):
        x, y = cell
        cell = (x + delta_x, y + delta_y)
      dest = cell
      target_elems = game.stage.get_elems_at(cell)
      target_elem = next((e for e in target_elems if e.breakable), None)
      target_actor = next((e for e in target_elems if isinstance(e, DungeonActor)), None)
      game.anims.append([PauseAnim(
        duration=5,
        on_start=lambda: (
          on_start and on_start(dest),
          user.core.anims.append(Mummy.ChargeAnim()),
          game.anims.append([pause_anim := PauseAnim()]),
          game.vfx.append(LinenVfx(
            src=user.cell,
            dest=dest,
            color=user.color(),
            on_connect=(lambda: game.attack(
              actor=user,
              target=target_actor,
              animate=False,
            )) if target_actor else (lambda: (
              target_elem.crush(game)
            )) if target_elem else None,
            on_end=lambda: (
              user.core.anims.clear(),
              pause_anim.end(),
              on_end and on_end(),
            )
          ))
        )
      )])

  class Backstep(SupportSkill):
    def effect(game, user, dest, on_start=None, on_end=None):
      dest_cell = add_vector(user.cell, invert_direction(user.facing))
      if is_cell_walkable_to_actor(stage=game.stage, cell=dest_cell, actor=user):
        game.anims.append([JumpAnim(
          target=user,
          src=user.cell,
          dest=dest_cell,
          height=6,
          duration=15,
          on_end=lambda: (
            setattr(user, "cell", dest_cell),
            setattr(user, "turns", 1),
            on_end and on_end()
          )
        )])
      else:
        on_end and on_end()

  def __init__(soldier, name="Tomb Trooper", *args, **kwargs):
    super().__init__(Core(
      name=name,
      faction="enemy",
      stats=Stats(
        hp=24,
        st=11,
        dx=9,
        ag=4,
        lu=3,
        en=12,
      ),
      skills=[Club],
      message=[(name, "I-I'm not doing all this because I want to, you know!")]
    ), *args, **kwargs)
    soldier.damaged = False

  def damage(soldier, *args, **kwargs):
    super().damage(*args, **kwargs)
    if not soldier.ailment == "poison":
      soldier.damaged = True

  def step(soldier, game):
    if not soldier.can_step():
      return None

    if not soldier.aggro:
      return super().step(game)

    enemy = game.find_closest_enemy(soldier)
    if not enemy:
      return None

    if random() < 1 / 32 and soldier.idle(game):
      return None

    if soldier.damaged:
      soldier.damaged = False
      soldier.face(enemy.cell)
      rear_cell = add_vector(soldier.cell, invert_direction(soldier.facing))
      if (randint(0, 1)
      and game.stage.is_cell_empty(rear_cell)
      and not game.stage.is_tile_at_pit(rear_cell)):
        return ("use_skill", Mummy.Backstep)
      else:
        return soldier.charge(skill=ClawRush, dest=enemy.cell)

    soldier_x, soldier_y = soldier.cell
    enemy_x, enemy_y = enemy.cell
    dist_x = enemy_x - soldier_x
    dist_y = enemy_y - soldier_y
    dist = abs(dist_x) + abs(dist_y)
    if (dist == 2 and (abs(dist_x) == 2 or abs(dist_y) == 2)
    or dist == 1 and randint(0, 1)):
      soldier.face(enemy.cell)
      return soldier.charge(skill=ClawRush, dest=enemy.cell)
    elif abs(dist_x) <= 2 and abs(dist_x) == abs(dist_y):
      return soldier.charge(skill=Mummy.LinenWhip, dest=enemy.cell)

    if is_adjacent(soldier.cell, enemy.cell):
      return ("attack", enemy)
    else:
      return ("move_to", enemy.cell)

  def view(soldier, anims):
    soldier_image = assets.sprites["soldier"]
    soldier_xoffset, soldier_yoffset = (0, 0)
    anim_group = [a for a in anims[0] if a.target is soldier] if anims else []
    anim_group += soldier.core.anims
    for anim in anim_group:
      if (type(anim) is StepAnim and anim.duration != PUSH_DURATION
      or type(anim) is AttackAnim):
        soldier_image = assets.sprites["soldier_move"]
        break
      elif type(anim) in (FlinchAnim, FlickerAnim):
        soldier_image = assets.sprites["soldier_flinch"]
        break
      elif type(anim) is Mummy.ChargeAnim:
        soldier_image = assets.sprites["soldier_charge"]
        soldier_xoffset += anim.offset
        break
    else:
      if soldier.ailment == "sleep" or soldier.get_hp() < soldier.get_hp_max() / 2:
        soldier_image = assets.sprites["soldier_sleep"]
      else:
        soldier_image = assets.sprites["soldier"]
    if soldier.ailment == "freeze":
      soldier_image = assets.sprites["soldier_flinch"]
    return super().view([Sprite(
      image=soldier_image,
      pos=(soldier_xoffset, soldier_yoffset)
    )], anims)
