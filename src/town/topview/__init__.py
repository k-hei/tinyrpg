import pygame
from pygame import Surface, SRCALPHA
from contexts import Context
from contexts.dialogue import DialogueContext
from contexts.shop import ShopContext
from hud import Hud
from assets import load as use_assets
from town.topview.stage import Stage, Tile
from town.topview.actor import Actor
from sprite import Sprite
from anims.tween import TweenAnim
from easing.expo import ease_out
from lib.lerp import lerp
from config import TILE_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT
import keyboard

def insert_value(mapping, key, value):
  keys = mapping.keys()
  values = [value if v == key else v for k, v in mapping.items()]
  return dict(zip(keys, values))

class TopViewContext(Context):
  class HudAnim(TweenAnim):
    def __init__(anim):
      super().__init__(duration=45)

  def __init__(ctx, area, hero):
    super().__init__()
    ctx.area = area
    ctx.hero = Actor(core=hero, facing=(0, -1))
    ctx.stage = area(ctx.hero)
    ctx.hud = Hud()
    ctx.elem = None
    ctx.link = None
    ctx.anims = []
    ctx.debug = False

  def handle_keydown(ctx, key):
    if ctx.child:
      return ctx.child.handle_keydown(key)
    if ctx.anims or ctx.link:
      return None
    if key in keyboard.ARROW_DELTAS:
      delta = keyboard.ARROW_DELTAS[key]
      return ctx.handle_move(delta)
    if keyboard.get_pressed(key) > 1:
      return None
    if key in (pygame.K_SPACE, pygame.K_RETURN):
      return ctx.handle_talk()
    if key == pygame.K_b and keyboard.get_pressed(pygame.K_LCTRL):
      return ctx.handle_debug()

  def handle_keyup(ctx, key):
    if ctx.child:
      return ctx.child.handle_keyup(key)
    if key in keyboard.ARROW_DELTAS:
      ctx.handle_stopmove()

  def handle_move(ctx, delta):
    ctx.hero.move(delta)
    ctx.collide(ctx.hero, delta)

  def handle_debug(ctx):
    ctx.debug = not ctx.debug

  def collide(ctx, actor, delta):
    delta_x, delta_y = delta
    stage = ctx.stage
    rect = actor.get_rect()
    init_center = rect.center
    elem_rects = [(e, e.get_rect()) for e in ctx.stage.elems if e is not actor and e.solid]
    elem, elem_rect = next(((e, r) for (e, r) in elem_rects if r.colliderect(rect)), (None, None))
    col_w = rect.left // ctx.stage.scale
    row_n = rect.top // ctx.stage.scale
    col_e = (rect.right - 1) // ctx.stage.scale
    row_s = (rect.bottom - 1) // ctx.stage.scale
    tile_nw = stage.get_tile_at((col_w, row_n))
    tile_ne = stage.get_tile_at((col_e, row_n))
    tile_sw = stage.get_tile_at((col_w, row_s))
    tile_se = stage.get_tile_at((col_e, row_s))
    above_half = rect.top < (row_n + 0.5) * ctx.stage.scale

    if delta_x < 0:
      if rect.centerx < 0:
        rect.centerx = 0
        ctx.handle_areachange((-1, 0))
      elif ((Tile.is_solid(tile_nw) or Tile.is_solid(tile_sw))
      or (Tile.is_halfsolid(tile_nw) or Tile.is_halfsolid(tile_sw))
      and above_half):
        rect.left = (col_w + 1) * ctx.stage.scale
      elif elem:
        rect.left = elem_rect.right
    elif delta_x > 0:
      if rect.centerx > WINDOW_WIDTH:
        rect.centerx = WINDOW_WIDTH
        ctx.handle_areachange((1, 0))
      elif ((Tile.is_solid(tile_ne) or Tile.is_solid(tile_se))
      or (Tile.is_halfsolid(tile_ne) or Tile.is_halfsolid(tile_se))
      and above_half):
        rect.right = col_e * ctx.stage.scale
      elif elem:
        rect.right = elem_rect.left

    if delta_y < 0:
      if rect.top < 0:
        rect.top = 0
        ctx.handle_areachange((0, -1))
      elif Tile.is_solid(tile_nw) or Tile.is_solid(tile_ne):
        rect.top = (row_n + 1) * ctx.stage.scale
      elif ((Tile.is_halfsolid(tile_nw) or Tile.is_halfsolid(tile_ne))
      and above_half):
        rect.top = (row_n + 0.5) * ctx.stage.scale
      elif elem:
        rect.top = elem_rect.bottom
    elif delta_y > 0:
      if rect.top > WINDOW_HEIGHT:
        rect.top = WINDOW_HEIGHT
        ctx.handle_areachange((0, 1))
      elif Tile.is_solid(tile_sw) or Tile.is_solid(tile_se):
        rect.bottom = row_s * ctx.stage.scale
      elif elem:
        rect.bottom = elem_rect.top

    if elem:
      ctx.elem = elem
      elem.effect(ctx)
    if rect.center != init_center:
      actor.pos = rect.midtop

  def handle_stopmove(ctx):
    ctx.hero.stop_move()
    if ctx.elem:
      ctx.elem.reset_effect()

  def handle_talk(ctx):
    hero = ctx.hero
    talkee = next((a for a in ctx.stage.elems if hero.can_talk(a)), None)
    if talkee is None:
      return False
    hero.stop_move()
    old_facing = talkee.get_facing()
    talkee.face(hero)
    message = talkee.next_message()
    if callable(message):
      message = message(talkee, ctx)
    if talkee.get_rect().centery >= WINDOW_WIDTH // 2:
      log_side = "top"
    else:
      log_side = "bottom"
    ctx.open(DialogueContext(
      script=message,
      lite=True,
      side=log_side,
      on_close=lambda: talkee.face(old_facing),
    ))
    return True

  def handle_areachange(ctx, delta):
    ctx.link = delta
    ctx.get_root().dissolve(on_clear=ctx.close)

  def update(ctx):
    super().update()
    if ctx.link:
      ctx.hero.move(ctx.link)
    for elem in ctx.stage.elems:
      elem.update()
    for anim in ctx.anims:
      if anim.done:
        ctx.anims.remove(anim)
      else:
        anim.update()

  def view(ctx, sprites):
    assets = use_assets()
    hero = ctx.hero
    sprites.append(Sprite(
      image=assets.sprites[ctx.area.bg_id],
      pos=(0, 0),
      layer="bg"
    ))
    def zsort(elem):
      _, y = elem.pos
      z = y
      if elem is hero:
        z -= 1
      return z
    elems = sorted(ctx.stage.elems, key=zsort)
    elem_sprites = []
    for elem in elems:
      if not ctx.child and hero.can_talk(elem):
        bubble_x, bubble_y = elem.get_rect().topright
        bubble_y -= TILE_SIZE // 4
        elem_sprites.append(Sprite(
          image=assets.sprites["bubble_talk"],
          pos=(bubble_x, bubble_y),
          origin=("left", "bottom"),
          layer="markers"
        ))
      elem.view(elem_sprites)
      if ctx.debug and not ctx.child:
        elem_sprites += debug_elem_view(elem)

    elem_sprites.sort(key=lambda sprite: (
      0 if sprite.layer == "bg"
      else 2 if sprite.layer == "markers"
      else 1
    ))
    sprites += elem_sprites

    if not ctx.child or type(ctx.child.child) is not ShopContext:
      hud_image = ctx.hud.update(ctx.hero.core)
      hud_x = 8
      hud_y = 8
      hud_anim = next((a for a in ctx.anims if type(a) is TopViewContext.HudAnim), None)
      if hud_anim:
        t = hud_anim.pos
        t = ease_out(t)
        hud_x = lerp(2, hud_x, t)
        hud_y = lerp(WINDOW_HEIGHT - 2 - hud_image.get_height(), hud_y, t)
      sprites.append(Sprite(
        image=hud_image,
        pos=(hud_x, hud_y),
        layer="hud"
      ))

    if ctx.child:
      ctx.child.view(sprites)

def debug_elem_view(elem):
  RED = 0x7FFF0000
  BLUE = 0x7F0000FF
  YELLOW = 0x7FFFFF00
  GREEN = 0x7F00FF00
  CIRCLE_RADIUS = 2
  CIRCLE_SIZE = (CIRCLE_RADIUS * 2, CIRCLE_RADIUS * 2)

  elem_rect = elem.get_rect()
  box_surface = Surface(elem_rect.size, SRCALPHA)
  box_color = RED if elem.solid else BLUE
  box_layer = "markers" if elem.solid else "bg"
  box_surface.fill(box_color)

  pos_circle = Surface(CIRCLE_SIZE, SRCALPHA)
  pygame.draw.circle(pos_circle, YELLOW, (CIRCLE_RADIUS, CIRCLE_RADIUS), CIRCLE_RADIUS)

  spawn_circle = Surface(CIRCLE_SIZE, SRCALPHA)
  pygame.draw.circle(spawn_circle, GREEN, (CIRCLE_RADIUS, CIRCLE_RADIUS), CIRCLE_RADIUS)

  return [
    Sprite(image=box_surface, pos=elem_rect.topleft, layer="hud"),
    # Sprite(image=spawn_circle, pos=elem.spawn_pos, layer="hud", origin=("center", "center")),
    Sprite(image=pos_circle, pos=elem.pos, layer="hud", origin=("center", "center")),
  ]
