import pygame
import lib.input as input
import lib.vector as vector
from contexts import Context
from contexts.explore.stageview import StageView
from config import WALK_DURATION

input.config({
  pygame.K_w: "up",
  pygame.K_a: "left",
  pygame.K_s: "down",
  pygame.K_d: "right",
  pygame.K_UP: "up",
  pygame.K_LEFT: "left",
  pygame.K_DOWN: "down",
  pygame.K_RIGHT: "right",
})

class ExploreContext(Context):
  def __init__(ctx, hero=None,stage=None, stage_view=None, *args, **kwargs):
    super().__init__(*args, **kwargs)
    ctx.party = [hero]
    ctx.stage = stage
    ctx.stage_view = stage_view or StageView(stage=stage)

  @property
  def hero(ctx):
    return ctx.party[0] if ctx.party else None

  def handle_press(ctx, button):
    delta = input.resolve_delta(button)
    if delta:
      return ctx.handle_move(delta)

  def handle_move(ctx, delta):
    if not ctx.hero:
      return

    ctx.move(ctx.hero, delta)

  def move(ctx, actor, delta):
    actor.facing = delta
    actor.pos = vector.add(
      actor.pos,
      vector.scale(
        delta,
        ctx.stage.tile_size / WALK_DURATION
      )
    )

  def update(ctx):
    for elem in ctx.stage.elems:
      elem.update(ctx)

  def view(ctx):
    return ctx.stage_view.view()
