import pygame
from contexts import Context
from contexts.dialogue import DialogueContext
from assets import load as use_assets
from building.stage import Stage, Tile
from building.actor import Actor
from cores.knight import KnightCore
from cores.mage import MageCore
from cores.rogue import RogueCore
from anims.walk import WalkAnim
from filters import replace_color
from palette import BLACK, BLUE, GREEN, ORANGE
from sprite import Sprite
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
        facing=(1, 0),
        color=GREEN,
        moving=True
      ),
      Actor(
        core=KnightCore(name="Arthur"),
        cell=(4, 1),
        facing=(0, 1),
        color=ORANGE,
        moving=True,
        move_period=45,
        is_shopkeep=True,
        message=lambda talkee, ctx: [
          (talkee.get_name(), "How can I help you?")
        ]
      )
    ]
    ctx.hero = ctx.actors[0]

  def handle_keydown(ctx, key):
    if ctx.child:
      return ctx.child.handle_keydown(key)
    if key in keyboard.ARROW_DELTAS:
      delta = keyboard.ARROW_DELTAS[key]
      return ctx.handle_move(delta)
    if keyboard.get_pressed(key) > 1:
      return None
    if key in (pygame.K_SPACE, pygame.K_RETURN):
      return ctx.handle_talk()

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
    init_center = rect.center
    other_rects = [a.get_rect() for a in ctx.actors if a is not actor]
    other_rect = next((r for r in other_rects if r.colliderect(rect)), None)
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
      elif other_rect:
        rect.left = other_rect.right
    elif delta_x > 0:
      if ((Tile.is_solid(tile_ne) or Tile.is_solid(tile_se))
      or (Tile.is_halfsolid(tile_ne) or Tile.is_halfsolid(tile_se))
      and above_half):
        rect.right = col_e * TILE_SIZE
      elif other_rect:
        rect.right = other_rect.left
    if delta_y < 0:
      if Tile.is_solid(tile_nw) or Tile.is_solid(tile_ne):
        rect.top = (row_n + 1) * TILE_SIZE
      elif ((Tile.is_halfsolid(tile_nw) or Tile.is_halfsolid(tile_ne))
      and above_half):
        rect.top = (row_n + 0.5) * TILE_SIZE
      elif other_rect:
        rect.top = other_rect.bottom
    elif delta_y > 0:
      if Tile.is_solid(tile_sw) or Tile.is_solid(tile_se):
        rect.bottom = row_s * TILE_SIZE
      elif other_rect:
        rect.bottom = other_rect.top
    if rect.center != init_center:
      actor.pos = rect.midtop

  def handle_stopmove(ctx):
    ctx.hero.stop_move()

  def handle_talk(ctx):
    hero = ctx.hero
    talkee = next((a for a in ctx.actors if hero.can_talk(a)), None)
    if talkee is None:
      return False
    hero.stop_move()
    old_facing = talkee.get_facing()
    talkee.face(hero)
    message = talkee.next_message()
    if callable(message):
      message = message(talkee, ctx)
    ctx.open(DialogueContext(
      script=message,
      lite=True,
      on_close=lambda: talkee.face(old_facing),
    ))
    return True

  def update(ctx):
    super().update()
    for actor in ctx.actors:
      actor.update()

  def draw(ctx, surface):
    assets = use_assets()
    hero = ctx.hero
    surface.blit(assets.sprites["shop"], (0, 0))
    sprites = []
    actors = sorted(ctx.actors, key=lambda actor: actor.pos[1] - 1 if actor is hero else actor.pos[1])
    for actor in actors:
      if not ctx.child and actor is not hero and hero.can_talk(actor):
        bubble_x, bubble_y = actor.get_rect().topright
        bubble_y -= TILE_SIZE // 4
        sprites.append(Sprite(
          image=assets.sprites["bubble_talk"],
          pos=(bubble_x, bubble_y),
          origin=("left", "bottom")
        ))
      actor.render().draw(surface)
    for sprite in sprites:
      sprite.draw(surface)
    if ctx.child:
      ctx.child.draw(surface)
