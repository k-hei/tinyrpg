from random import random, randint, choice
from lib.cell import is_adjacent, manhattan, neighborhood

from dungeon.actors import DungeonActor
from cores.ghost import Ghost as GhostCore

from skills.weapon.tackle import Tackle
from skills.support import SupportSkill
from skills.ailment.somnus import Somnus

from anims.step import StepAnim
from anims.attack import AttackAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from anims.warpin import WarpInAnim
from anims.pause import PauseAnim
from helpers.stage import is_cell_walkable_to_actor

from lib.sprite import Sprite
import assets
from skills import Skill
from items.materials.luckychoker import LuckyChoker
from vfx.ghostarm import GhostArmVfx
from locations.desert.elems.snake import DesertSnake


class Ghost(DungeonActor):
  skill = Somnus
  drops = [LuckyChoker]
  idle_messages = [
    "The {enemy} emits a cold aura.",
    "The {enemy} eyes your wallet.",
    "The {enemy} giggles.",
  ]

  class Warp(SupportSkill):
    def effect(game, user, dest=None, on_start=None, on_end=None):
      hero = game.hero
      if not hero:
        return on_end and on_end()

      if not dest:
        valid_cells = [c for c in hero.visible_cells
          if c != user.cell
          and game.camera.is_cell_visible(c)
          and is_cell_walkable_to_actor(game.stage, cell=c, actor=user)
          and c in game.room.cells]

        if not valid_cells:
          return on_end and on_end()

        dest = choice(valid_cells)

      game.anims.append([FlickerAnim(
        target=user,
        duration=15,
        on_end=lambda: game.anims[-1].append(WarpInAnim(
          target=user,
          on_start=lambda: (
            setattr(user, "cell", dest),
          ),
          on_end=on_end
        )),
      )])

  class ColdWhip(Skill):
    name = "ColdWhip"
    charge_turns = 1

    def effect(game, user, dest, on_start=None, on_end=None):
      target_actor = next((e for e in game.stage.get_elems_at(dest) if isinstance(e, DungeonActor)), None)
      user.core.anims = [GhostCore.WhipAnim()]
      game.anims.append([
        pause_anim := PauseAnim(on_end=on_end),
        PauseAnim(
          duration=14,
          on_start=lambda: on_start and on_start(),
          on_end=lambda: game.vfx.append(
            GhostArmVfx(
              cell=dest,
              color=user.color(),
              on_connect=(lambda: game.attack(
                actor=user,
                target=target_actor,
                animate=False,
              )) if target_actor else None,
              on_end=pause_anim.end,
            )
          )
        )
      ])
      return False

  def __init__(ghost, *args, **kwargs):
    super().__init__(GhostCore(
      skills=[Tackle, Somnus]
    ), floating=True, *args, **kwargs)
    ghost.damaged = False

  def damage(ghost, *args, **kwargs):
    super().damage(*args, **kwargs)

    if ghost.ailment == "poison":
      return

    ghost.damaged = True
    if random() < 1 / 2 and not (ghost.charge_skill is Somnus
    and is_adjacent(ghost.cell, ghost.charge_dest)):
      ghost.reset_charge()

  def charge(ghost, *args, **kwargs):
    if next((False for a in ghost.core.anims if isinstance(a, GhostCore.ChargeAnim)), True):
      ghost.core.anims.append(GhostCore.ChargeAnim())
    return super().charge(*args, **kwargs)

  def find_warp_dest(ghost, game, enemy):
    valid_cells = [n for n in neighborhood(enemy.cell, radius=randint(1, 2))
      if n != ghost.cell
      and is_cell_walkable_to_actor(game.stage, n, ghost)
      and n in game.room.cells]
    return choice(valid_cells) if valid_cells else None

  def charge_warp_skill(ghost, game, enemy, warp_dest):
    skill = choice((
      *([Somnus] * (3 if enemy.hp <= enemy.hp_max / 2 else 1)
        if not enemy.ailment == "sleep"
          and is_adjacent(warp_dest, enemy.cell)
        else []),
      Ghost.Warp,
      Ghost.ColdWhip
    ))
    if skill is Somnus:
      ghost.face(enemy.cell)
      ghost.charge(skill=Somnus, dest=enemy.cell, turns=1)
    elif skill is Ghost.Warp:
      ghost.charge(skill=Ghost.Warp)
    elif skill is Ghost.ColdWhip:
      ghost.charge(skill=Ghost.ColdWhip, dest=enemy.cell)

  def step(ghost, game):
    if not ghost.can_step():
      return None

    if not ghost.aggro:
      return super().step(game)

    enemy = game.find_closest_enemy(ghost)
    if not enemy:
      return None

    idle_chance = 1 / 4 if enemy.ailment == "sleep" else 1 / 16
    if random() < idle_chance and ghost.idle(game):
      ghost.core.anims.append(GhostCore.LaughAnim(duration=75))
      return None

    if ghost.damaged:
      ghost.damaged = False
      ghost.turns = 0
      warp_dest = (ghost.find_warp_dest(game, enemy)
        if random() < 1 / 2
        else None)

      if warp_dest:
        ghost.charge_warp_skill(game, enemy, warp_dest)

      return ("use_skill", Ghost.Warp, warp_dest)

    if (is_adjacent(ghost.cell, enemy.cell)
    and ghost.hp <= ghost.hp_max / 2
    and not enemy.ailment == "sleep"):
      ghost.face(enemy.cell)
      return ghost.charge(skill=Somnus, dest=enemy.cell, turns=1)

    if manhattan(ghost.cell, enemy.cell) <= 2:
      if random() < 1 / 2:
        return ghost.charge(skill=Ghost.ColdWhip, dest=enemy.cell)
      else:
        warp_dest = ghost.find_warp_dest(game, enemy)
        if warp_dest:
          ghost.charge_warp_skill(game, enemy, warp_dest)
        return ("use_skill", Ghost.Warp, warp_dest)

    movement_type = choice(("strafe", "strafe", "move_to", "warp", "wait"))
    if movement_type == "strafe":
      delta = DesertSnake.find_move_delta(ghost, goal=enemy.cell)
      return ("move", delta)
    elif movement_type == "move_to":
      return ("move_to", enemy.cell)
    elif movement_type == "warp":
      ghost.turns = 0
      return ("use_skill", Ghost.Warp)
    elif movement_type == "wait":
      return ("wait",)

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

      if (isinstance(anim, FlinchAnim)
      or isinstance(anim, FlickerAnim) and ghost.dead):
        ghost_image = assets.sprites["ghost_flinch"]

      if isinstance(anim, GhostCore.LaughAnim):
        ghost_image = anim.frame()
        break

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
