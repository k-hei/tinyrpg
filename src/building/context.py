from contexts import Context
from assets import load as use_assets
from building.stage import Stage, Tile
from building.actor import Actor
from cores.knight import KnightCore
from cores.mage import MageCore
from cores.rogue import RogueCore
from anims.walk import WalkAnim
from filters import replace_color
from palette import BLACK, BLUE, GREEN, ORANGE
from config import TILE_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT
import keyboard

class BuildingContext(Context):
  def __init__(ctx):
    super().__init__()
    ctx.stage = Stage.parse([
      "########",
      "#.#....#",
      "#.####.#",
      "#.''''.#",
      "#......#",
      "#......#",
      "########",
    ])
    ctx.actors = [
      Actor(core=MageCore(), cell=(2, 5), facing=(0, -1)),
      Actor(
        core=RogueCore(),
        cell=(6, 5),
        facing=(-1, 0),
        color=GREEN,
        moving=True
      ),
      Actor(
        core=KnightCore(),
        cell=(4, 1),
        facing=(0, 1),
        color=ORANGE,
        moving=True,
        move_period=45
      )
    ]
    ctx.hero = ctx.actors[0]

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
    stage = ctx.stage
    rect = actor.get_rect()
    col_w = rect.left // TILE_SIZE
    row_n = rect.top // TILE_SIZE
    col_e = (rect.right - 1) // TILE_SIZE
    row_s = (rect.bottom - 1) // TILE_SIZE
    tile_nw = stage.get_tile_at((col_w, row_n))
    tile_ne = stage.get_tile_at((col_e, row_n))
    tile_sw = stage.get_tile_at((col_w, row_s))
    tile_se = stage.get_tile_at((col_e, row_s))
    above_half = rect.top < (row_n + 0.5) * TILE_SIZE
    if delta_x < 0:
      if ((Tile.is_solid(tile_nw) or Tile.is_solid(tile_sw))
      or (Tile.is_halfsolid(tile_nw) or Tile.is_halfsolid(tile_sw))
      and above_half):
        rect.left = (col_w + 1) * TILE_SIZE
        actor.pos = rect.midtop
    elif delta_x > 0:
      if ((Tile.is_solid(tile_ne) or Tile.is_solid(tile_se))
      or (Tile.is_halfsolid(tile_ne) or Tile.is_halfsolid(tile_se))
      and above_half):
        rect.right = col_e * TILE_SIZE
        actor.pos = rect.midtop
    if delta_y < 0:
      if Tile.is_solid(tile_nw) or Tile.is_solid(tile_ne):
        rect.top = (row_n + 1) * TILE_SIZE
        actor.pos = rect.midtop
      elif ((Tile.is_halfsolid(tile_nw) or Tile.is_halfsolid(tile_ne))
      and above_half):
        rect.top = (row_n + 0.5) * TILE_SIZE
        actor.pos = rect.midtop
    elif delta_y > 0:
      if Tile.is_solid(tile_sw) or Tile.is_solid(tile_se):
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
    actors = sorted(ctx.actors, key=lambda actor: actor.pos[1] + 1 if actor is ctx.hero else actor.pos[1])
    for actor in actors:
      actor.render().draw(surface)
