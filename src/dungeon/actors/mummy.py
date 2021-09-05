from random import randint
from dungeon.actors import DungeonActor
from cores import Core, Stats
from skills.attack import AttackSkill
from skills.weapon.club import Club
from lib.cell import is_adjacent, add as add_vector
from lib.compose import compose
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
        game.vfx.append(ClawVfx(cell=target_cell))
        if target_actor:
          game.attack(
            actor=user,
            target=target_actor,
            modifier=1.5,
            is_chaining=True,
            on_end=on_end
          )
        else:
          game.anims[0].append(AttackAnim(
            target=user,
            src=dest_cell,
            dest=target_cell,
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
      target_actor = next((e for e in game.floor.get_elems_at(dest) if isinstance(e, DungeonActor)), None)
      not game.anims and game.anims.append([])
      game.anims[0].append(AttackAnim(
        target=user,
        src=user.cell,
        dest=dest
      ))
      game.vfx.append(LinenVfx(
        src=user.cell,
        dest=dest,
        on_connect=(lambda: game.attack(
          actor=user,
          target=target_actor,
          is_ranged=True,
          is_chaining=True,
          is_animated=False,
        )) if target_actor else None,
        on_end=on_end
      ))

  def __init__(soldier):
    super().__init__(Core(
      name="Mummy",
      faction="enemy",
      stats=Stats(
        hp=11,
        st=12,
        dx=9,
        ag=4,
        lu=3,
        en=13,
      ),
      skills=[ Club ]
    ))

  def step(soldier, game):
    enemy = game.find_closest_enemy(soldier)
    if enemy is None:
      return None

    soldier_x, soldier_y = soldier.cell
    enemy_x, enemy_y = enemy.cell
    dist_x = enemy_x - soldier_x
    dist_y = enemy_y - soldier_y
    if abs(dist_x) + abs(dist_y) == 2 and (abs(dist_x) == 2 or abs(dist_y) == 2):
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
      if type(anim) is MoveAnim and anim.duration != PUSH_DURATION:
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
