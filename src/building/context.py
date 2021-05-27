from contexts import Context
from assets import load as use_assets
from building.stage import Stage
from building.actor import Actor
from cores.knight import KnightCore
from cores.mage import MageCore
from anims.walk import WalkAnim
from filters import replace_color
from palette import BLACK, BLUE, ORANGE
from config import TILE_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT
import keyboard

class BuildingContext(Context):
  def __init__(ctx):
    super().__init__()
    ctx.hero = Actor(core=MageCore(), cell=(2, 5), facing=(0, -1))
    ctx.shopkeep = Actor(core=KnightCore(), cell=(4, 1), facing=(0, 1), color=ORANGE)
    ctx.shopkeep.move_duration = 45
    ctx.shopkeep.start_move()
    ctx.actors = [ctx.hero, ctx.shopkeep]
    ctx.stage = Stage([
      [1, 1, 1, 1, 1, 1, 1, 1],
      [1, 0, 1, 0, 0, 0, 0, 1],
      [1, 0, 1, 1, 1, 1, 0, 1],
      [1, 0, 0, 0, 0, 0, 0, 1],
      [1, 0, 0, 0, 0, 0, 0, 1],
      [1, 0, 0, 0, 0, 0, 0, 1],
      [1, 1, 1, 1, 1, 1, 1, 1]
    ])

  def handle_keydown(ctx, key):
    if key in keyboard.ARROW_DELTAS:
      delta = keyboard.ARROW_DELTAS[key]
      ctx.handle_move(delta)

  def handle_keyup(ctx, key):
    if key in keyboard.ARROW_DELTAS:
      ctx.handle_stopmove()

  def handle_move(ctx, delta):
    ctx.hero.move(delta)
    ctx.collide(ctx.hero, delta)

  def collide(ctx, actor, delta):
    delta_x, delta_y = delta
    rect = actor.get_rect()
    col_w = rect.left // TILE_SIZE
    row_n = rect.top // TILE_SIZE
    col_e = (rect.right - 1) // TILE_SIZE
    row_s = (rect.bottom - 1) // TILE_SIZE
    if delta_x < 0:
      tile_nw = ctx.stage.get_tile_at((col_w, row_n))
      tile_sw = ctx.stage.get_tile_at((col_w, row_s))
      if tile_nw or tile_sw:
        rect.left = (col_w + 1) * TILE_SIZE
        actor.pos = rect.midtop
    elif delta_x > 0:
      tile_ne = ctx.stage.get_tile_at((col_e, row_n))
      tile_se = ctx.stage.get_tile_at((col_e, row_s))
      if tile_ne or tile_se:
        rect.right = col_e * TILE_SIZE
        actor.pos = rect.midtop
    if delta_y < 0:
      tile_nw = ctx.stage.get_tile_at((col_w, row_n))
      tile_ne = ctx.stage.get_tile_at((col_e, row_n))
      if tile_nw or tile_ne:
        rect.top = (row_n + 1) * TILE_SIZE
        actor.pos = rect.midtop
    elif delta_y > 0:
      tile_sw = ctx.stage.get_tile_at((col_w, row_s))
      tile_se = ctx.stage.get_tile_at((col_e, row_s))
      if tile_sw or tile_se:
        rect.bottom = row_s * TILE_SIZE
        actor.pos = rect.midtop

  def handle_stopmove(ctx):
    ctx.hero.stop_move()

  def update(ctx):
    super().update()
    for actor in ctx.actors:
      actor.update()

  def draw(ctx, surface):
    sprites = use_assets().sprites
    surface.blit(sprites["shop"], (0, 0))
    for actor in ctx.actors:
      actor.render().draw(surface)
