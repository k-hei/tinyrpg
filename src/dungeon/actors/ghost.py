from random import randint
from dungeon.actors import DungeonActor
from cores.ghost import Ghost as GhostCore
from skills.weapon.tackle import Tackle
from anims.move import MoveAnim
from anims.attack import AttackAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from anims.pause import PauseAnim
from sprite import Sprite
import assets
from skills import Skill
from lib.cell import is_adjacent, manhattan
from skills.ailment.somnus import Somnus
from vfx.ghostarm import GhostArmVfx

class Ghost(DungeonActor):
  class ColdWhip(Skill):
    name = "ColdWhip"
    chant_turns = 2
    def effect(user, dest, game, on_end=None):
      target_elem = next((e for e in game.floor.get_elems_at(dest) if isinstance(e, DungeonActor)), None)
      user.core.anims = [GhostCore.WhipAnim(on_end=on_end if target_elem is None else None)]
      game.anims.append([PauseAnim(
        duration=14,
        on_end=lambda: game.vfx.append(
          GhostArmVfx(
            cell=dest,
            on_connect=(lambda: (
              game.flinch(
                target=target_elem,
                damage=game.find_damage(user, target_elem, 1.25),
                on_end=on_end
              )
            )) if target_elem else None
          )
        )
      )])

  skill = Somnus

  def __init__(ghost, chant_skill=None, chant_dest=None, chant_turns=0, *args, **kwargs):
    super().__init__(GhostCore(
      skills=[Tackle, Somnus]
    ), *args, **kwargs)
    ghost.chant_skill = chant_skill
    ghost.chant_dest = chant_dest
    ghost.chant_turns = chant_turns

  def set_faction(ghost, faction):
    super().set_faction(faction)
    ghost.reset_chant()

  def reset_chant(ghost):
    ghost.chant_skill = None
    ghost.chant_dest = None
    ghost.chant_turns = 0
    ghost.stats.ag = ghost.core.stats.ag
    ghost.stats.lu = ghost.core.stats.lu

  def chant(ghost, skill, dest, game):
    ghost.stats.ag = game.hero.stats.ag
    ghost.stats.lu = 0
    ghost.chant_skill = skill
    ghost.chant_dest = dest
    ghost.chant_turns = skill.chant_turns
    ghost.core.anims.append(GhostCore.ChargeAnim())

  def cast(ghost):
    if ghost.chant_skill is None:
      return None
    command = ("use_skill", ghost.chant_skill, ghost.chant_dest)
    ghost.reset_chant()
    return command

  def step(ghost, game):
    enemy = game.find_closest_enemy(ghost)
    if enemy is None:
      return False

    if ghost.chant_turns:
      ghost.chant_turns -= 1
      if ghost.chant_turns == 0:
        return ghost.cast()
      else:
        return None

    if is_adjacent(ghost.cell, enemy.cell) and not enemy.ailment == "sleep" and randint(1, 5) == 1:
      ghost.face(enemy.cell)
      ghost.turns = 0
      return ("use_skill", Somnus)
    elif manhattan(ghost.cell, enemy.cell) <= 2:
      return ghost.chant(
        game=game,
        skill=Ghost.ColdWhip,
        dest=game.hero.cell
      )
    else:
      return ("move_to", enemy.cell)

  def view(ghost, anims):
    ghost_image = assets.sprites["ghost"]
    anim_group = [a for a in anims[0] if a.target is ghost] if anims else []
    anim_group += ghost.core.anims
    offset_x, offset_y = (0, 0)
    for anim in anim_group:
      if type(anim) in (MoveAnim, AttackAnim):
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
