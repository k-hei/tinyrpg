import pygame
from pygame import Surface, SRCALPHA
from contexts import Context
from contexts.dialogue import DialogueContext
from contexts.shop import ShopContext
from contexts.inventory import InventoryContext
from comps.hud import Hud
from assets import load as use_assets
from town.topview.stage import Stage, Tile
from town.topview.actor import Actor
from lib.sprite import Sprite
from anims.tween import TweenAnim
from easing.expo import ease_out
from lib.lerp import lerp
from lib.filters import outline
from transits.dissolve import DissolveIn, DissolveOut
from colors.palette import BLACK, WHITE
import lib.keyboard as keyboard
import lib.gamepad as gamepad
from cores.knight import Knight
from cores.mage import Mage
from config import TILE_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT, LABEL_FRAMES

def insert_value(mapping, key, value):
  keys = mapping.keys()
  values = [value if v == key else v for k, v in mapping.items()]
  return dict(zip(keys, values))

class TopViewContext(Context):
  class HudAnim(TweenAnim):
    def __init__(anim):
      super().__init__(duration=45)

  def __init__(ctx, store, area=None, spawn=None):
    super().__init__()
    ctx.store = store
    ctx.area = area
    ctx.party = [Actor(core=c, facing=(0, -1), solid=(i == 0)) for i, c in enumerate(store.party)]
    ctx.stage = area and area(ctx.party)
    ctx.hud = Hud(store.party)
    ctx.elem = None
    ctx.link = None
    ctx.anims = []
    ctx.debug = False
    ctx.time = 0
    ctx.comps = [ctx.hud]

  def handle_press(ctx, button):
    if ctx.child:
      return ctx.child.handle_press(button)
    if ctx.anims or ctx.link or ctx.get_head().transits:
      return None

    directions = not button and [d for d in (gamepad.controls.LEFT, gamepad.controls.RIGHT, gamepad.controls.UP, gamepad.controls.DOWN) if gamepad.get_state(d)]
    if directions:
      directions = sorted(directions, key=lambda d: gamepad.get_state(d))
      button = directions[0]
    delta = keyboard.ARROW_DELTAS[button] if button in keyboard.ARROW_DELTAS else None
    if delta:
      return ctx.handle_move(delta)

    if keyboard.get_state(button) + gamepad.get_state(button) > 1:
      return None
    if button in (pygame.K_SPACE, pygame.K_RETURN, gamepad.controls.confirm):
      return ctx.handle_talk()
    if button == pygame.K_b and keyboard.get_state(pygame.K_LCTRL):
      return ctx.handle_debug()

  def handle_release(ctx, button):
    if ctx.child:
      return ctx.child.handle_release(button)
    if button in keyboard.ARROW_DELTAS:
      ctx.handle_stopmove()

  def handle_move(ctx, delta):
    hero, *allies = ctx.party
    hero.move(delta)
    if not ctx.collide(hero, delta):
      for i, ally in enumerate(allies):
        ally.follow(ctx.party[i])

  def handle_debug(ctx):
    ctx.debug = not ctx.debug
    return True

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
      return True
    else:
      return False

  def handle_stopmove(ctx):
    for actor in ctx.party:
      actor.stop_move()
    if ctx.elem:
      ctx.elem.reset_effect()

  def handle_talk(ctx):
    hero, *_ = ctx.party
    talkee = next((a for a in ctx.stage.elems if hero.can_talk(a)), None)
    if talkee is None:
      return False
    for actor in ctx.party:
      actor.stop_move()
    old_facing = talkee.facing
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

  def get_graph(ctx):
    return ctx.parent.graph if "graph" in dir(ctx.parent) else None

  def handle_areachange(ctx, delta):
    ctx.link = delta
    ctx.get_head().transition([
      DissolveIn(on_end=lambda: ctx.change_areas(ctx.area.links["entrance"])),
      DissolveOut()
    ])

  def change_areas(ctx, link):
    if graph := ctx.get_graph():
      dest_link = graph.tail(head=link)
      if dest_link:
        dest_area = graph.link_area(link=dest_link)
        for actor in ctx.party:
          actor.stop_move()
        ctx.parent.load_area(dest_area, dest_link)
    else:
      ctx.close()

  def switch_chars(ctx):
    ctx.store.switch_chars()
    ctx.party.reverse()

  def recruit(ctx, actor):
    ctx.store.recruit(actor.core)
    if len(ctx.party) == 1:
      ctx.party.append(actor)
    else:
      # TODO: handle party replacement
      ctx.party[1] = actor

  def update(ctx):
    super().update()

    if ctx.link:
      for actor in ctx.party:
        actor.move(ctx.link)

    for elem in ctx.stage.elems:
      elem.update()

    for anim in ctx.anims:
      if anim.done:
        ctx.anims.remove(anim)
      else:
        anim.update()

    for comp in ctx.comps:
      comp.updated = False
      comp.update()

    ctx.time += 1

  def view(ctx):
    sprites = []
    assets = use_assets()
    hero, *_ = ctx.party
    sprites.append(Sprite(
      image=assets.sprites[ctx.area.bg],
      pos=(0, 0),
      layer="bg"
    ))
    if ctx.area.fg:
      sprites.append(Sprite(
        image=assets.sprites[ctx.area.fg],
        pos=(0, 0),
        layer="bg"
      ))
    def zsort(elem):
      _, y = elem.pos
      z = y
      if elem is hero:
        z += 1
      return z
    elems = sorted(ctx.stage.elems, key=zsort)
    for elem in elems:
      if elem.pos is None:
        continue
      if not ctx.child and hero.can_talk(elem):
        bubble_x, bubble_y = elem.get_rect().topright
        bubble_y -= TILE_SIZE // 4
        sprites.append(Sprite(
          image=assets.sprites["bubble_talk"][0],
          pos=(bubble_x, bubble_y),
          origin=("left", "bottom"),
          layer="markers"
        ))
      elem_sprites = elem.view()
      elem_sprite = elem_sprites and elem_sprites[0]
      if elem_sprite and not ctx.stage.dark:
        elem_sprite.image = outline(elem_sprite.image, WHITE)
      sprites += elem_sprites
      if ctx.debug and not ctx.child:
        sprites += debug_elem_view(elem)

    if ctx.debug and not ctx.child:
      for cell in ctx.stage.get_cells():
        if ctx.stage.get_tile_at(cell).solid:
          sprites += debug_tile_view(cell, ctx.stage.scale)

    sprites.sort(key=lambda sprite: (
      0 if sprite.layer == "bg"
      else 2 if sprite.layer == "markers"
      else 1
    ))

    if ctx.link or (ctx.child
      and not isinstance(ctx.child, DialogueContext)
      and not isinstance(ctx.child, InventoryContext)
      and not isinstance(ctx.child.child, ShopContext)
    ):
      ctx.hud.active and ctx.hud.exit()
    else:
      not ctx.hud.active and ctx.hud.enter()

    for sprite in sprites:
      sprite.move((256 - WINDOW_WIDTH // 2, 0))

    sprites += ctx.hud.view()

    if ctx.time < LABEL_FRAMES and not ctx.child:
      label_image = assets.ttf["normal"].render(ctx.area.name, WHITE)
      label_image = outline(label_image, BLACK)
      if not ctx.area.dark:
        label_image = outline(label_image, WHITE)
      sprites.append(Sprite(
        image=label_image,
        pos=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 4),
        origin=("center", "center"),
        layer="markers"
      ))

    return sprites + super().view()

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

def debug_tile_view(cell, scale):
  col, row = cell
  box_surface = Surface((scale, scale), SRCALPHA)
  box_surface.fill(0x7F0000FF)
  return [
    Sprite(image=box_surface, pos=(col * scale, row * scale), layer="hud")
  ]
