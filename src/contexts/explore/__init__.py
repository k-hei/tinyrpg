import pygame
from pygame import Surface, SRCALPHA
from lib.sprite import Sprite
import lib.vector as vector
import lib.input as input
from lib.compose import compose
from helpers.findactor import find_actor
from contexts import Context
from contexts.explore.stageview import StageView
from contexts.dungeon.camera import Camera
from contexts.inventory import InventoryContext
from dungeon.actors import DungeonActor
from dungeon.props.itemdrop import ItemDrop
from vfx.talkbubble import TalkBubble
from anims.item import ItemAnim
from anims.attack import AttackAnim
from tiles import Tile
from config import WINDOW_SIZE, COMBAT_THRESHOLD

class ExploreContext(Context):
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
    ctx.debug = False

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
  def talkbubble(ctx):
    return next((v for v in ctx.vfx if type(v) is TalkBubble), None)

  def enter(ctx):
    ctx.camera.focus(ctx.hero)

  def open(ctx, child, on_close=None):
    if type(child) is InventoryContext:
      open = super().open
      ctx.parent.hud.enter(on_end=lambda: (
        open(child, on_close=compose(
          ctx.parent.hud.exit,
          on_close
        ))
      ))
    else:
      return super().open(child, on_close)

  def handle_press(ctx, button):
    if ctx.child:
      return ctx.child.handle_press(button)

    if ctx.anims:
      return

    if not button:
      delta = input.resolve_delta()
      delta and ctx.handle_move(
        delta=delta,
        running=input.get_state(input.CONTROL_RUN) > 0
      )

    if input.get_state(button) > 1:
      return False

    control = input.resolve_control(button)
    if control == input.CONTROL_CONFIRM:
      ctx.handle_action()

  def handle_release(ctx, button):
    delta = input.resolve_delta(button)
    if delta:
      return ctx.hero.stop_move()

  def handle_move(ctx, delta, running=False):
    if not ctx.hero:
      return

    delta_x, delta_y = delta
    diagonal = delta_x and delta_y

    if delta_x:
      ctx.move(ctx.hero, delta=(delta_x, 0), diagonal=diagonal, running=running)
      ctx.collide(ctx.hero, delta=(delta_x, 0))

    if delta_y:
      ctx.move(ctx.hero, delta=(0, delta_y), diagonal=diagonal, running=running)
      ctx.collide(ctx.hero, delta=(0, delta_y))

    prop = next((e for e in ctx.stage.elems if
      isinstance(e, ItemDrop) # TODO: design generic model for steppables
      and ctx.hero.rect.colliderect(e.rect)
    ), None)
    if prop:
      prop.effect(ctx, ctx.hero)
      ctx.hero.stop_move()

    room = next((r for r in ctx.stage.rooms if ctx.hero.cell in r.cells), None)
    enemy = next((e for e in ctx.stage.elems if
      isinstance(e, DungeonActor)
      and e.faction == DungeonActor.FACTION_ENEMY
      and room and e.cell in room.cells
    ), None)
    if enemy:
      return ctx.handle_combat()

  def move(ctx, actor, delta, diagonal=False, running=False):
    actor.move(delta, diagonal, running)

  def collide(ctx, actor, delta):
    delta_x, delta_y = delta
    stage = ctx.stage
    rect = actor.rect
    init_center = rect.center
    elem_rects = [(e, e.rect) for e in stage.elems if e is not actor and e.solid]
    elem, elem_rect = next(((e, r) for (e, r) in elem_rects if r.colliderect(rect)), (None, None))
    col_w = rect.left // stage.tile_size
    row_n = rect.top // stage.tile_size
    col_e = (rect.right - 1) // stage.tile_size
    row_s = (rect.bottom - 1) // stage.tile_size
    tile_nw = stage.get_tile_at((col_w, row_n))
    tile_ne = stage.get_tile_at((col_e, row_n))
    tile_sw = stage.get_tile_at((col_w, row_s))
    tile_se = stage.get_tile_at((col_e, row_s))

    if delta_x < 0:
      if Tile.is_solid(tile_nw) or Tile.is_solid(tile_sw):
        rect.left = (col_w + 1) * stage.tile_size
      elif elem:
        rect.left = elem_rect.right
    elif delta_x > 0:
      if Tile.is_solid(tile_ne) or Tile.is_solid(tile_se):
        rect.right = col_e * stage.tile_size
      elif elem:
        rect.right = elem_rect.left

    if delta_y < 0:
      if Tile.is_solid(tile_nw) or Tile.is_solid(tile_ne):
        rect.top = (row_n + 1) * stage.tile_size
      elif elem:
        rect.top = elem_rect.bottom
    elif delta_y > 0:
      if Tile.is_solid(tile_sw) or Tile.is_solid(tile_se):
        rect.bottom = row_s * stage.tile_size
      elif elem:
        rect.bottom = elem_rect.top

    if rect.center != init_center:
      actor.pos = rect.midtop
      return True
    else:
      return False

  def handle_obtain(ctx, item, target, on_end=None):
    obtained = ctx.store.obtain(item)
    if obtained:
      old_facing = ctx.hero.facing
      ctx.hero.facing = (0, 1)
      ctx.anims.append([
        ItemAnim(
          target=target,
          item=item(),
          duration=60,
          on_end=lambda: (
            setattr(ctx.hero, "facing", old_facing),
            on_end and on_end(),
          )
        )
      ])
      ctx.parent.minilog.print(message=("Obtained ", item().token(), "."))
    return obtained

  def handle_action(ctx):
    facing_elem = ctx.parent.facing_elem
    if facing_elem is None:
      return False

    ctx.anims.append([
      AttackAnim(
        target=ctx.hero,
        src=ctx.hero.cell,
        dest=facing_elem.cell,
        on_connect=lambda: (
          facing_elem.effect(ctx, ctx.hero),
          ctx.parent.update_bubble(),
        )
      )
    ])
    return True

  def handle_combat(ctx):
    ctx.on_end and ctx.on_end()

  def view(ctx):
    if not ctx._headless:
      return super().view()

    sprites = ctx.stage_view.view()
    if ctx.debug:
      sprites += [debug_view_elem(e) for e in ctx.stage.elems]

    return sprites + super().view()

def debug_view_elem(elem):
  ALPHA = 128
  RED = (255, 0, 0, ALPHA)
  BLUE = (0, 0, 255, ALPHA)
  YELLOW = (255, 255, 0, ALPHA)
  GREEN = (0, 255, 0, ALPHA)
  CIRCLE_RADIUS = 2
  CIRCLE_SIZE = (CIRCLE_RADIUS * 2, CIRCLE_RADIUS * 2)

  hitbox_surface = Surface(elem.rect.size, flags=SRCALPHA)
  hitbox_surface.fill(BLUE)

  origin_circle = Surface(CIRCLE_SIZE, SRCALPHA)
  pygame.draw.circle(origin_circle, YELLOW, (CIRCLE_RADIUS, CIRCLE_RADIUS), CIRCLE_RADIUS)

  return [Sprite(
    image=hitbox_surface,
    pos=elem.rect.topleft,
  ), Sprite(
    image=origin_circle,
    pos=elem.pos,
    origin=Sprite.ORIGIN_CENTER,
  )]
