from random import randint
import lib.vector as vector
import lib.input as input
from lib.direction import invert as invert_direction
from helpers.findactor import find_actor

from contexts import Context
from contexts.dungeon.camera import Camera
from contexts.explore.stageview import StageView
from comps.damage import DamageValue
from dungeon.actors import DungeonActor
from tiles import Tile
from anims.move import MoveAnim
from anims.step import StepAnim
from anims.attack import AttackAnim
from anims.flinch import FlinchAnim
from anims.pause import PauseAnim
from anims.flicker import FlickerAnim
from colors.palette import GOLD
from config import (
  WINDOW_SIZE,
  FLINCH_PAUSE_DURATION, FLICKER_DURATION, NUDGE_DURATION
)

def find_damage_text(damage):
  if damage == 0:
    return "BLOCK"
  elif damage == None:
    return "MISS"
  else:
    return int(damage)

class CombatContext(Context):
  def __init__(ctx, store, stage, stage_view=None, on_end=None, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx._headless = stage_view is None
    if stage_view:
      ctx.stage = stage_view.stage
      ctx.camera = stage_view.camera
      ctx.stage_view = stage_view
    else:
      ctx.stage = stage
      ctx.camera = Camera(WINDOW_SIZE)
      ctx.stage_view = StageView(stage=stage, camera=ctx.camera)
    ctx.store = store
    ctx.on_end = on_end

  @property
  def hero(ctx):
    return find_actor(
      char=ctx.store.party[0],
      stage=ctx.stage
    ) if ctx.store.party else None

  @property
  def anims(ctx):
    return ctx.stage_view.anims

  @property
  def vfx(ctx):
    return ctx.stage_view.vfx

  def enter(ctx):
    if not ctx.hero:
      return
    x, y = ctx.hero.pos
    if x % ctx.hero.scale or y % ctx.hero.scale:
      hero_dest = vector.scale(
        vector.add((0.5, 0.5), ctx.hero.cell),
        ctx.hero.scale
      )
      ctx.anims.append([MoveAnim(
        target=ctx.hero,
        src=ctx.hero.pos,
        dest=hero_dest,
        speed=2,
        on_end=lambda: (
          ctx.anims.append([
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

  def handle_press(ctx, button):
    if ctx.anims:
      return

    delta = input.resolve_delta(button)
    if delta:
      return ctx.handle_move(delta)

    button = input.resolve_button(button)
    if input.get_state(button) > 1:
      return

    if button == input.BUTTON_A:
      return ctx.handle_attack()

  def handle_move(ctx, delta):
    moved = ctx.move(ctx.hero, delta)
    if moved:
      return True
    else:
      ctx.hero.facing = delta
      return False

  def move(ctx, actor, delta):
    target_cell = vector.add(actor.cell, delta)

    target_tile = ctx.stage.get_tile_at(target_cell)
    if Tile.is_solid(target_tile):
      return False

    target_elem = (
      next((e for e in ctx.stage.get_elems_at(target_cell) if e.solid), None)
      or next((e for e in ctx.stage.get_elems_at(target_cell)), None)
    )
    if target_elem and target_elem.solid:
      return False

    ctx.anims.append([StepAnim(
      target=actor,
      src=actor.cell,
      dest=target_cell,
    )])
    actor.cell = target_cell
    return True

  def handle_attack(ctx):
    target_cell = vector.add(ctx.hero.cell, ctx.hero.facing)
    target_actor = next((e for e in ctx.stage.get_elems_at(target_cell) if isinstance(e, DungeonActor)), None)
    return ctx.attack(actor=ctx.hero, target=target_actor)

  def attack(ctx, actor, target=None, modifier=1):
    if target:
      actor.face(target.cell)
      damage = ctx.find_damage(actor, target, modifier)
      crit = ctx.find_crit(actor, target)

    attack_delay = (actor.core.AttackAnim.frames_duration[0]
      if "AttackAnim" in dir(actor.core) and actor.facing == (0, 1)
      else 0
    )
    ctx.anims.append([AttackAnim(
      target=actor,
      delay=attack_delay,
      src=actor.cell,
      dest=vector.add(actor.cell, actor.facing),
      on_connect=lambda: target and ctx.flinch(
        target=target,
        damage=damage,
        crit=crit,
        direction=actor.facing,
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
      ctx.vfx.append(DamageValue(
        text="CRITICAL!",
        cell=target.cell,
        offset=(4, -4),
        color=GOLD,
        delay=15
      ))
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
        on_end=lambda: target.is_dead() and ctx.kill(target)
      )
    ]

  def kill(ctx, target):
    target.kill(ctx)
    ctx.anims[0].append(FlickerAnim(
      target=target,
      duration=FLICKER_DURATION,
      on_end=lambda: ctx.stage.elems.remove(target),
    ))

  def nudge(ctx, actor, direction):
    source_cell = actor.cell
    target_cell = vector.add(source_cell, direction)
    actor.cell = target_cell
    not ctx.anims and ctx.anims.append([])
    ctx.anims[0].append(StepAnim(
      duration=NUDGE_DURATION,
      target=actor,
      src=source_cell,
      dest=target_cell
    ))
    return True
