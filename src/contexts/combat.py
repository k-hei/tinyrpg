import lib.vector as vector
import lib.input as input
from helpers.findactor import find_actor

from contexts import Context
from contexts.dungeon.camera import Camera
from contexts.explore.stageview import StageView
from tiles import Tile
from anims.move import MoveAnim
from anims.step import StepAnim
from config import WINDOW_SIZE

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

  def enter(ctx):
    if not ctx.hero:
      return
    x, y = ctx.hero.pos
    if x % ctx.hero.scale or y % ctx.hero.scale:
      hero_dest = vector.scale(
        vector.add((0.5, 0.5), ctx.hero.cell),
        ctx.hero.scale
      )
      ctx.stage_view.anims.append([MoveAnim(
        target=ctx.hero,
        src=ctx.hero.pos,
        dest=hero_dest,
        speed=2,
        on_end=lambda: (
          ctx.stage_view.anims.append([
            ctx.hero.core.BrandishAnim(target=ctx.hero)
          ]),
          ctx.hero.anims.clear(),
          ctx.hero.core.anims.clear(),
          ctx.hero.core.anims.append(
            ctx.hero.core.IdleDownAnim(),
          )
        )
      )])
      ctx.hero.pos = hero_dest

  def handle_press(ctx, button):
    if button and ctx.stage_view.anims:
      return

    delta = input.resolve_delta(button)
    if delta:
      return ctx.handle_move(delta)

  def handle_move(ctx, delta):
    return ctx.move(ctx.hero, delta)

  def move(ctx, actor, delta):
    target_cell = vector.add(actor.cell, delta)
    target_tile = ctx.stage.get_tile_at(target_cell)
    if Tile.is_solid(target_tile):
      return False

    ctx.stage_view.anims.append([StepAnim(
      target=actor,
      src=actor.cell,
      dest=target_cell,
    )])
    actor.cell = target_cell
