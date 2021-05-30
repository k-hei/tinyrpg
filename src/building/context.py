import pygame
from contexts import Context
from contexts.dialogue import DialogueContext
from contexts.prompt import PromptContext, Choice
from assets import load as use_assets
from building.stage import Stage, Tile
from building.actor import Actor
from cores.knight import KnightCore
from cores.mage import MageCore
from cores.rogue import RogueCore
from palette import GREEN, ORANGE
from sprite import Sprite
from config import TILE_SIZE, WINDOW_WIDTH, WINDOW_HEIGHT
import keyboard

class BuildingContext(Context):
  def __init__(ctx):
    super().__init__()
    ctx.hero = Actor(core=MageCore(), cell=(2, 5), facing=(0, -1))
    ctx.stage = Stage.parse([
      "###+####",
      "#.#.2..#",
      "#.####.#",
      "#.''''.#",
      "#......#",
      "#.0...1#",
      "##+#####",
    ], {
      "0": ctx.hero,
      "1": Actor(
        core=RogueCore(),
        cell=(6, 5),
        facing=(1, 0),
        color=GREEN,
        moving=True,
        message=lambda talkee, ctx: [
          (talkee.get_name(), "You know what I can't get enough of?"),
          (talkee.get_name(), "BBWs."),
          (talkee.get_name(), "Big beautiful wings.....")
        ]
      ),
      "2": Actor(
        core=KnightCore(name="Arthur"),
        cell=(4, 1),
        facing=(0, 1),
        color=ORANGE,
        moving=True,
        move_period=45,
        is_shopkeep=True,
        message=lambda talkee, ctx: (
          ctx.hero.get_rect().centery > talkee.get_rect().centery and [
            shop := PromptContext(
              message="{}: How can I help you?".format(talkee.get_name().upper()),
              choices=[
                Choice("Buy items"),
                Choice("Sell items"),
                Choice("Nothing", closing=True)
              ],
              required=True,
              on_close=lambda choice: (
                choice and choice.text == "Buy items" and [
                  "This feature isn't implemented yet...",
                  shop
                ] or choice and choice.text == "Sell items" and [
                  "This feature isn't implemented yet...",
                  shop
                ]
              )
            ),
          ] or [
            (talkee.get_name(), "Aha nooo, we can'tttt"),
            (talkee.get_name(), "Not during business hours...")
          ]
        )
      )
    })
    ctx.elem = None
    ctx.anims = []
    ctx.link_direction = None

  def handle_keydown(ctx, key):
    if ctx.child:
      return ctx.child.handle_keydown(key)
    if ctx.anims or ctx.link_direction:
      return None
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
    elem_rects = [(e, e.get_rect()) for e in ctx.stage.elems if e is not actor and e.solid]
    elem, elem_rect = next(((e, r) for (e, r) in elem_rects if r.colliderect(rect)), (None, None))
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
      if rect.centerx < 0:
        rect.centerx = 0
        ctx.handle_areachange((-1, 0))
      elif ((Tile.is_solid(tile_nw) or Tile.is_solid(tile_sw))
      or (Tile.is_halfsolid(tile_nw) or Tile.is_halfsolid(tile_sw))
      and above_half):
        rect.left = (col_w + 1) * TILE_SIZE
      elif elem:
        rect.left = elem_rect.right
    elif delta_x > 0:
      if rect.centerx > WINDOW_WIDTH:
        rect.centerx = WINDOW_WIDTH
        ctx.handle_areachange((1, 0))
      elif ((Tile.is_solid(tile_ne) or Tile.is_solid(tile_se))
      or (Tile.is_halfsolid(tile_ne) or Tile.is_halfsolid(tile_se))
      and above_half):
        rect.right = col_e * TILE_SIZE
      elif elem:
        rect.right = elem_rect.left

    if delta_y < 0:
      if rect.top < 0:
        rect.top = 0
        ctx.handle_areachange((0, -1))
      elif Tile.is_solid(tile_nw) or Tile.is_solid(tile_ne):
        rect.top = (row_n + 1) * TILE_SIZE
      elif ((Tile.is_halfsolid(tile_nw) or Tile.is_halfsolid(tile_ne))
      and above_half):
        rect.top = (row_n + 0.5) * TILE_SIZE
      elif elem:
        rect.top = elem_rect.bottom
    elif delta_y > 0:
      if rect.top > WINDOW_HEIGHT:
        rect.top = WINDOW_HEIGHT
        ctx.handle_areachange((0, 1))
      elif Tile.is_solid(tile_sw) or Tile.is_solid(tile_se):
        rect.bottom = row_s * TILE_SIZE
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
    ctx.link_direction = delta
    ctx.get_root().dissolve(on_clear=ctx.close)

  def update(ctx):
    super().update()
    if ctx.link_direction:
      ctx.hero.move(ctx.link_direction)
    for elem in ctx.stage.elems:
      elem.update()
    for anim in ctx.anims:
      if anim.done:
        ctx.anims.remove(anim)
      anim.update()

  def draw(ctx, surface):
    assets = use_assets()
    hero = ctx.hero
    surface.blit(assets.sprites["shop"], (0, 0))
    sprites = []
    def zsort(elem):
      _, y = elem.pos
      z = y
      if elem is hero:
        z -= 1
      if not elem.solid:
        z -= WINDOW_HEIGHT
      return z
    elems = sorted(ctx.stage.elems, key=zsort)
    for elem in elems:
      if not ctx.child and hero.can_talk(elem):
        bubble_x, bubble_y = elem.get_rect().topright
        bubble_y -= TILE_SIZE // 4
        sprites.append(Sprite(
          image=assets.sprites["bubble_talk"],
          pos=(bubble_x, bubble_y),
          origin=("left", "bottom")
        ))
      elem.render().draw(surface)
    for sprite in sprites:
      sprite.draw(surface)
    if ctx.child:
      ctx.child.draw(surface)