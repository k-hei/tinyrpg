from random import randint
import lib.vector as vector
import lib.input as input
from lib.direction import invert as invert_direction, normal as normalize_direction
from lib.compose import compose

from contexts.explore.base import ExploreBase
from comps.damage import DamageValue
from dungeon.actors import DungeonActor
from tiles import Tile
import tiles.default as tileset
from anims.move import MoveAnim
from anims.step import StepAnim
from anims.attack import AttackAnim
from anims.jump import JumpAnim
from anims.flinch import FlinchAnim
from anims.pause import PauseAnim
from anims.flicker import FlickerAnim
from vfx.flash import FlashVfx
from colors.palette import GOLD
from config import (
  MOVE_DURATION, FLINCH_PAUSE_DURATION, FLICKER_DURATION, NUDGE_DURATION,
  CRIT_MODIFIER,
)

def find_damage_text(damage):
  if damage == 0:
    return "BLOCK"
  elif damage == None:
    return "MISS"
  else:
    return int(damage)

class CombatContext(ExploreBase):

  def enter(ctx):
    if not ctx.hero:
      return

    x, y = ctx.hero.pos
    if x % ctx.hero.scale or y % ctx.hero.scale:
      hero_dest = vector.scale(
        vector.add(ctx.hero.cell, (0.5, 0.5)),
        ctx.hero.scale
      )
      ctx.anims.append([MoveAnim(
        target=ctx.hero,
        src=ctx.hero.pos,
        dest=hero_dest,
        speed=2,
        on_end=lambda: (
          ctx.anims.append([
            # TODO: switch to actor animation queues
            ctx.hero.core.BrandishAnim(
              target=ctx.hero,
              on_end=lambda: (
                ctx.hero.anims.clear(),
                ctx.hero.core.anims.clear(),
                ctx.hero.core.anims.append(
                  ctx.hero.core.IdleDownAnim(),
                )
              )
            )
          ]),
        )
      )])
      ctx.hero.pos = hero_dest

  def exit(ctx):
    ctx.exiting = True
    ctx.hud.exit(on_end=lambda: (
      ctx.hero.core.anims.clear(),
      ctx.close()
    ))

  def handle_press(ctx, button):
    if ctx.child:
      return ctx.child.handle_press(button)

    if ctx.anims or ctx.exiting:
      return

    delta = input.resolve_delta(button, fixed_axis=True)
    if delta != (0, 0):
      return ctx.handle_move(delta)

    button = input.resolve_button(button)
    if button == input.BUTTON_A:
      return ctx.handle_action()

    if input.get_state(button) > 1:
      return

  def handle_move(ctx, delta):
    target_cell = vector.add(ctx.hero.cell, delta)
    target_tile = ctx.stage.get_tile_at(target_cell)

    def on_move():
      target_elem = next((e for e in ctx.stage.get_elems_at(ctx.hero.cell) if not isinstance(e, DungeonActor)), None)
      target_elem and target_elem.effect(ctx, ctx.hero)

    ctx.hero.facing = delta
    moved = ctx.move(ctx.hero, delta, on_end=on_move)
    if moved:
      return True
    elif issubclass(target_tile, tileset.Pit):
      return ctx.leap(actor=ctx.hero, on_end=on_move)
    else:
      return False

  def move(ctx, actor, delta, jump=False, on_end=None):
    target_cell = vector.add(actor.cell, delta)
    target_tile = ctx.stage.get_tile_at(target_cell)
    if not Tile.is_walkable(target_tile):
      return False

    target_elem = (
      next((e for e in ctx.stage.get_elems_at(target_cell) if e.solid), None)
      or next((e for e in ctx.stage.get_elems_at(target_cell)), None)
    )
    if target_elem and target_elem.solid:
      return False

    move_duration = MOVE_DURATION
    move_duration = move_duration * 1.5 if jump else move_duration
    move_kind = JumpAnim if jump else StepAnim
    ctx.anims.append([move_anim := move_kind(
      target=actor,
      src=actor.cell,
      dest=target_cell,
      duration=move_duration,
      on_end=compose(ctx.update_bubble, on_end)
    )])
    move_anim.update() # initial update to ensure animation loops seamlessly
    if jump:
      ctx.anims[-1].append(PauseAnim(duration=move_duration + 5))

    ctx.update_bubble()
    actor.cell = target_cell
    actor.facing = normalize_direction(delta)
    return True

  def leap(ctx, actor, on_end=None):
    delta = vector.scale(actor.facing, 2)
    moved = ctx.move(actor, delta, jump=True, on_end=on_end)
    return moved

  def handle_action(ctx):
    facing_actor = ctx.facing_actor
    if isinstance(facing_actor, DungeonActor) and facing_actor.faction == "enemy":
      return ctx.handle_attack()

    facing_elem = ctx.facing_elem
    action_result = facing_elem.effect(ctx, ctx.hero) if facing_elem else False
    if action_result != None:
      not ctx.anims and ctx.anims.append([])
      ctx.anims[0].insert(0, AttackAnim(
        target=ctx.hero,
        src=ctx.hero.cell,
        dest=vector.add(ctx.hero.cell, ctx.hero.facing),
      ))
      ctx.update_bubble()

    return action_result

  def handle_attack(ctx):
    target_cell = vector.add(ctx.hero.cell, ctx.hero.facing)
    target_actor = next((e for e in ctx.stage.get_elems_at(target_cell) if isinstance(e, DungeonActor)), None)
    return ctx.attack(actor=ctx.hero, target=target_actor)

  def attack(ctx, actor, target=None, modifier=1):
    if target:
      actor.face(target.cell)
      crit = ctx.find_crit(actor, target)
      if crit:
        damage = ctx.find_damage(actor, target, modifier=modifier * CRIT_MODIFIER)
      else:
        damage = ctx.find_damage(actor, target, modifier)

    attack_delay = (
      actor.core.AttackAnim.frames_duration[0]
        if "AttackAnim" in dir(actor.core) and actor.facing == (0, 1)
        else 0
    )
    ctx.anims.append([AttackAnim(
      target=actor,
      delay=attack_delay,
      src=actor.cell,
      dest=vector.add(actor.cell, actor.facing),
      on_connect=lambda: target and (
        target.alert(cell=actor.cell),
        ctx.flinch(
          target=target,
          damage=damage,
          crit=crit,
          direction=actor.facing,
        )
      )
    )])
    actor.attack()
    return True

  def find_damage(ctx, actor, target, modifier=1):
    actor_st = actor.st * modifier
    target_en = target.en
    variance = 1
    return max(1, actor_st - target_en + randint(-variance, variance))

  def find_crit(ctx, actor, target):
    return (
      target.ailment == DungeonActor.AILMENT_SLEEP
      or actor.facing == target.facing
    )

  def flinch(ctx, target, damage, direction, crit=False):
    show_text = lambda: ctx.vfx.append(DamageValue(
      text=find_damage_text(damage),
      cell=target.cell,
    ))

    if damage and crit:
      ctx.vfx.extend([
        DamageValue(
          text="CRITICAL!",
          cell=target.cell,
          offset=(4, -4),
          color=GOLD,
          delay=15
        ),
        FlashVfx()
      ])
      ctx.stage_view.shake(vertical=bool(direction[1]))
      direction and ctx.nudge(target, direction)

    not ctx.anims and ctx.anims.append([])
    ctx.anims[0] += [
      FlinchAnim(
        target=target,
        direction=direction,
        on_start=lambda: (
          setattr(target, "facing", invert_direction(direction)),
          target.damage(damage),
          show_text(),
        )
      ),
      PauseAnim(
        duration=FLINCH_PAUSE_DURATION,
        on_end=lambda: (
          (target.is_dead() or issubclass(ctx.stage.get_tile_at(target.cell), tileset.Pit)) and ctx.kill(target)
        )
      )
    ]

  def kill(ctx, target):
    target.kill(ctx)
    ctx.exiting = not ctx.find_enemies_in_range()
    ctx.anims[0].append(FlickerAnim(
      target=target,
      duration=FLICKER_DURATION,
      on_end=lambda: (
        ctx.stage.elems.remove(target),
        ctx.exiting and ctx.exit()
      )
    ))

  def nudge(ctx, actor, direction, on_end=None):
    source_cell = actor.cell
    target_cell = vector.add(source_cell, direction)
    target_tile = ctx.stage.get_tile_at(target_cell)
    if not ctx.stage.is_cell_empty(target_cell) and not issubclass(target_tile, tileset.Pit):
      return False

    actor.cell = target_cell
    not ctx.anims and ctx.anims.append([])
    ctx.anims[0].append(StepAnim(
      duration=NUDGE_DURATION,
      target=actor,
      src=source_cell,
      dest=target_cell,
      on_end=on_end
    ))
    return True
