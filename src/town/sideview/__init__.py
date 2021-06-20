from math import sin, pi
import pygame
from contexts import Context
from town.sideview.actor import Actor
from cores.knight import KnightCore
from assets import load as use_assets
from sprite import Sprite
from config import TILE_SIZE
from filters import replace_color
from palette import BLACK, BLUE

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
    ctx.time = 0

  def init(ctx):
    ctx.spawn()
    ctx.area.init(ctx)

  def spawn(ctx):
    ctx.area.spawn(ctx.hero, (32, 0))

  def handle_keydown(ctx, key):
    if key in (pygame.K_LEFT, pygame.K_a):
      return ctx.hero.move((-1, 0))
    if key in (pygame.K_RIGHT, pygame.K_d):
      return ctx.hero.move((1, 0))

  def handle_keyup(ctx, key):
    if key in (pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d):
      return ctx.hero.stop_move()

  def update(ctx):
    ctx.hero.update()
    ctx.time += 1

  def view(ctx, sprites):
    assets = use_assets().sprites
    sprites += ctx.area.view(ctx.hero)
    link = find_nearby_link(ctx.hero, ctx.area.links)
    if link and (link.direction == (0, -1) or link.direction == (0, 1)):
      arrow_image = (link.direction == (0, -1)
        and assets["link_north"]
        or assets["link_south"]
      )
      arrow_image = replace_color(arrow_image, BLACK, BLUE)
      arrow_y = ARROW_Y + sin(ctx.time % ARROW_PERIOD / ARROW_PERIOD * 2 * pi) * ARROW_BOUNCE
      sprites += [Sprite(
        image=arrow_image,
        pos=(link.x + ctx.area.camera, arrow_y),
        origin=("center", "center")
      )]
