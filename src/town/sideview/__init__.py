from math import sin, pi
import pygame
from contexts import Context
from contexts.dialogue import DialogueContext
from town.sideview.actor import Actor
from cores.knight import KnightCore
from assets import load as use_assets
from sprite import Sprite
from config import TILE_SIZE
from filters import replace_color
from palette import BLACK, BLUE

def can_talk(hero, actor):
  if (not actor.get_message()
  or actor.get_faction() == "player"):
    return False
  hero_x, _ = hero.pos
  actor_x, _ = actor.pos
  dist_x = actor_x - hero_x
  facing_x, _ = hero.get_facing()
  return abs(dist_x) < TILE_SIZE * 1.5 and dist_x * facing_x >= 0

def find_nearby_npc(hero, actors):
  return next((a for a in actors if can_talk(hero, a)), None)

def find_nearby_link(hero, links):
  hero_x, _ = hero.pos
  for link in links.values():
    dist_x = link.x - hero_x
    _, direction_y = link.direction
    if abs(dist_x) < TILE_SIZE // 2 and direction_y:
      return link

ARROW_Y = 168
ARROW_PERIOD = 45
ARROW_BOUNCE = 2

class SideViewContext(Context):
  def __init__(ctx, area, party=[]):
    super().__init__()
    ctx.area = area
    ctx.hero = Actor(core=party and party[0] or KnightCore())
    ctx.link = None
    ctx.talkee = None
    ctx.nearby_link = None
    ctx.nearby_npc = None
    ctx.time = 0

  def init(ctx):
    ctx.spawn()
    ctx.area.init(ctx)

  def spawn(ctx):
    ctx.area.spawn(ctx.hero, (64, 0))

  def handle_move(ctx, delta):
    ctx.hero.move((delta, 0))

  def handle_talk(ctx):
    ctx.nearby_npc and print(type(ctx.nearby_npc.core).__name__)
    if ctx.nearby_npc is None:
      return False
    ctx.talkee = ctx.nearby_npc
    talkee = ctx.nearby_npc
    hero = ctx.hero
    hero.stop_move()
    old_facing = talkee.get_facing()
    talkee.face(hero)
    message = talkee.get_message()
    if callable(message):
      message = message(ctx)
    def stop_talk():
      talkee.face(old_facing)
      ctx.talkee = None
    ctx.open(DialogueContext(script=message, on_close=stop_talk))
    return True

  def handle_keydown(ctx, key):
    if ctx.child:
      return ctx.child.handle_keydown(key)
    if key in (pygame.K_LEFT, pygame.K_a):
      return ctx.handle_move(-1)
    if key in (pygame.K_RIGHT, pygame.K_d):
      return ctx.handle_move(1)
    if key in (pygame.K_SPACE, pygame.K_RETURN):
      return ctx.handle_talk()

  def handle_keyup(ctx, key):
    if key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d):
      return ctx.hero.stop_move()

  def update(ctx):
    ctx.nearby_link = find_nearby_link(ctx.hero, ctx.area.links)
    ctx.nearby_npc = find_nearby_npc(ctx.hero, ctx.area.actors) if ctx.nearby_link is None else None
    ctx.hero.update()
    ctx.time += 1

  def view(ctx):
    sprites = []
    assets = use_assets().sprites
    sprites += ctx.area.view(ctx.hero)
    if ctx.child:
      sprites += ctx.child.view()
    elif link := ctx.nearby_link:
      arrow_image = (link.direction == (0, -1)
        and assets["link_north"]
        or assets["link_south"]
      )
      arrow_image = replace_color(arrow_image, BLACK, BLUE)
      arrow_y = ARROW_Y + sin(ctx.time % ARROW_PERIOD / ARROW_PERIOD * 2 * pi) * ARROW_BOUNCE
      sprites += [Sprite(
        image=arrow_image,
        pos=(link.x + ctx.area.camera, arrow_y),
        origin=("center", "center"),
        layer="markers"
      )]
    elif npc := ctx.nearby_npc:
      npc_sprite = next((s for s in sprites if s.target is npc), None)
      npc_x, npc_y = npc_sprite.pos
      bubble_image = assets["bubble_talk"]
      bubble_x = npc_x + TILE_SIZE * 0.25
      bubble_y = npc_y - TILE_SIZE * 0.75
      sprites.append(Sprite(
        image=bubble_image,
        pos=(bubble_x, bubble_y),
        layer="markers"
      ))
    return sprites
