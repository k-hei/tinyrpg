from random import randint
from dungeon.actors import DungeonActor
from cores import Core, Stats
from dungeon.stage import Tile
from skills.attack import AttackSkill
from skills.support import SupportSkill
from skills.weapon.club import Club
from lib.cell import is_adjacent, add as add_vector
from lib.compose import compose
from lib.direction import invert
from sprite import Sprite
import assets
from anims.move import MoveAnim
from anims.jump import JumpAnim
from anims.attack import AttackAnim
from anims.shake import ShakeAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from items.materials.crownjewel import CrownJewel
from vfx.claw import ClawVfx
from vfx.linen import LinenVfx
from config import PUSH_DURATION

class Mummy(DungeonActor):
  drops = [CrownJewel]

  class ChargeAnim(ShakeAnim): pass

  class ClawRush(AttackSkill):
    name = "ClawRush"
    charge_turns = 1
    def effect(user, dest, game, on_end=None):
      origin_cell = user.cell
      dest_cell = add_vector(origin_cell, user.facing)
      if game.floor.is_cell_empty(dest_cell):
        target_cell = add_vector(dest_cell, user.facing)
      else:
        target_cell = dest_cell
        dest_cell = origin_cell
      target_actor = next((e for e in game.floor.get_elems_at(target_cell) if isinstance(e, DungeonActor)), None)
      def attack():
        not game.anims and game.anims.append([])
        game.anims[0].append(AttackAnim(
          target=user,
          src=dest_cell,
          dest=target_cell,
          on_start=lambda: game.vfx.append(ClawVfx(cell=target_cell)),
          on_connect=(lambda: game.attack(
            actor=user,
            target=target_actor,
            modifier=1.5,
            is_animated=False
          )) if target_actor else None,
          on_end=on_end
        ))
      if dest_cell == origin_cell:
        attack()
      else:
        game.anims.append([
          MoveAnim(
            target=user,
            src=origin_cell,
            dest=dest_cell,
            duration=10,
            on_end=lambda: (
              setattr(user, "cell", dest_cell),
              attack()
            )
          )
        ])

  class LinenWhip(AttackSkill):
    name = "LinenWhip"
    def effect(user, dest, game, on_end=None):
      user_x, user_y = user.cell
      dest_x, dest_y = dest
      dist_x = dest_x - user_x
      dist_y = dest_y - user_y
      delta_x = dist_x // abs(dist_x)
      delta_y = dist_y // abs(dist_y)
      cell = (user_x + delta_x, user_y + delta_y)
      while (cell != dest
      and not Tile.is_solid(game.floor.get_tile_at(cell))
      and not [e for e in game.floor.get_elems_at(cell) if e.solid]):
        x, y = cell
        cell = (x + delta_x, y + delta_y)
      dest = cell
      target_actor = next((e for e in game.floor.get_elems_at(dest) if isinstance(e, DungeonActor)), None)
      user.core.anims.append(Mummy.ChargeAnim())
      game.vfx.append(LinenVfx(
        src=user.cell,
        dest=dest,
        color=user.color(),
        on_connect=(lambda: game.attack(
          actor=user,
          target=target_actor,
          is_ranged=True,
          is_chaining=True,
          is_animated=False,
        )) if target_actor else None,
        on_end=lambda: (
          user.core.anims.clear(),
          on_end and on_end()
        )
      ))

  class Backstep(SupportSkill):
    def effect(user, dest, game, on_end=None):
      dest_cell = add_vector(user.cell, invert(user.facing))
      if game.floor.is_cell_empty(dest_cell):
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

  def __init__(soldier, *args, **kwargs):
    super().__init__(Core(
      name="Mummy",
      faction="enemy",
      stats=Stats(
        hp=24,
        st=12,
        dx=9,
        ag=4,
        lu=3,
        en=12,
      ),
      skills=[ Club ]
    ), *args, **kwargs)
    soldier.damaged = False

  def damage(soldier, *args, **kwargs):
    super().damage(*args, **kwargs)
    if not soldier.ailment == "poison":
      soldier.damaged = True

  def step(soldier, game):
    enemy = game.find_closest_enemy(soldier)
    if enemy is None:
      return None

    if soldier.damaged:
      soldier.damaged = False
      soldier.face(enemy.cell)
      if randint(0, 1):
        return ("use_skill", Mummy.Backstep)
      else:
        return soldier.charge(skill=Mummy.ClawRush, dest=enemy.cell)

    soldier_x, soldier_y = soldier.cell
    enemy_x, enemy_y = enemy.cell
    dist_x = enemy_x - soldier_x
    dist_y = enemy_y - soldier_y
    dist = abs(dist_x) + abs(dist_y)
    if (dist == 2 and (abs(dist_x) == 2 or abs(dist_y) == 2)
    or dist == 1 and randint(0, 1)):
      soldier.face(enemy.cell)
      return soldier.charge(skill=Mummy.ClawRush, dest=enemy.cell)
    elif abs(dist_x) <= 2 and abs(dist_x) == abs(dist_y):
      return ("use_skill", Mummy.LinenWhip, enemy.cell)

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
      if (type(anim) is MoveAnim and anim.duration != PUSH_DURATION
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
      if soldier.ailment == "sleep":
        soldier_image = assets.sprites["soldier_sleep"]
      else:
        soldier_image = assets.sprites["soldier"]
    if soldier.ailment == "freeze":
      soldier_image = assets.sprites["soldier_flinch"]
    return super().view([Sprite(
      image=soldier_image,
      pos=(soldier_xoffset, soldier_yoffset)
    )], anims)
