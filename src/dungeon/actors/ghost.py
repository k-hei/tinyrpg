from random import randint
from dungeon.actors import DungeonActor
from cores.ghost import Ghost as GhostCore
from skills.weapon.tackle import Tackle
from anims.step import StepAnim
from anims.attack import AttackAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from anims.pause import PauseAnim
from lib.sprite import Sprite
import assets
from skills import Skill
from lib.cell import is_adjacent, manhattan
from skills.ailment.somnus import Somnus
from items.materials.luckychoker import LuckyChoker
from vfx.ghostarm import GhostArmVfx

class Ghost(DungeonActor):
  skill = Somnus
  drops = [LuckyChoker]

  class ColdWhip(Skill):
    name = "ColdWhip"
    charge_turns = 2
    def effect(user, dest, game, on_end=None):
      target_actor = next((e for e in game.floor.get_elems_at(dest) if isinstance(e, DungeonActor)), None)
      user.core.anims = [GhostCore.WhipAnim(on_end=on_end if target_actor is None else None)]
      game.anims.append([PauseAnim(
        duration=14,
        on_end=lambda: game.vfx.append(
          GhostArmVfx(
            cell=dest,
            color=user.color(),
            on_connect=(lambda: game.attack(
              actor=user,
              target=target_actor,
              is_ranged=True,
              is_animated=False,
              on_end=on_end
            )) if target_actor else None
          )
        )
      )])
      return False

  def __init__(ghost, *args, **kwargs):
    super().__init__(GhostCore(
      skills=[Tackle, Somnus]
    ), floating=True, *args, **kwargs)
    ghost.damaged = False

  def damage(ghost, *args, **kwargs):
    super().damage(*args, **kwargs)
    if not ghost.ailment == "poison":
      ghost.damaged = True
      ghost.turns = -1

  def charge(ghost, *args, **kwargs):
    super().charge(*args, **kwargs)
    ghost.core.anims.append(GhostCore.ChargeAnim())

  def step(ghost, game):
    enemy = game.find_closest_enemy(ghost)
    if not ghost.aggro:
      return super().step(game)
    if not enemy:
      return None

    if ghost.damaged:
      ghost.damaged = False
      if is_adjacent(ghost.cell, enemy.cell) and not enemy.ailment == "sleep" and randint(1, 5) == 1:
        ghost.face(enemy.cell)
        ghost.turns = 0
        return ("use_skill", Somnus)

    if manhattan(ghost.cell, enemy.cell) <= 2:
      return ghost.charge(skill=Ghost.ColdWhip, dest=enemy.cell)
    else:
      return ("move_to", enemy.cell)

  def view(ghost, anims):
    ghost_image = assets.sprites["ghost"]
    if ghost.ailment == "freeze":
      return super().view([Sprite(image=assets.sprites["ghost_flinch"])], anims)
    elif ghost.ailment == "sleep" or ghost.get_hp() < ghost.get_hp_max() / 2:
      ghost_image = assets.sprites["ghost_move"]
    anim_group = [a for a in anims[0] if a.target is ghost] if anims else []
    anim_group += ghost.core.anims
    offset_x, offset_y = (0, 0)
    for anim in anim_group:
      if type(anim) in (StepAnim, AttackAnim):
        ghost_image = assets.sprites["ghost_move"]
      elif type(anim) in (FlinchAnim, FlickerAnim):
        ghost_image = assets.sprites["ghost_flinch"]
      if type(anim) is GhostCore.ChargeAnim:
        ghost_image = assets.sprites["ghost_move"]
        offset_x += anim.offset
      if type(anim) is GhostCore.WhipAnim and anim.frame() == anim.frames[-1]:
        offset_x += anim.time // 2 % 2
    return ghost.core.view(
      sprites=super().view([Sprite(
        image=ghost_image,
        pos=(offset_x, offset_y)
      )], anims),
      anims=anim_group
    )
