import pygame
from contexts import Context
from town.sideview.actor import Actor
from cores.knight import KnightCore
from assets import load as use_assets
from sprite import Sprite

class SideViewContext(Context):
  def __init__(ctx, area, party=[]):
    super().__init__()
    ctx.area = area
    ctx.hero = Actor(core=party and party[0] or KnightCore())
    ctx.link = None

  def init(ctx):
    ctx.spawn()

  def spawn(ctx):
    ctx.hero.pos = (32, 0)

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

  def view(ctx, sprites):
    bg_x = ctx.area.view(sprites, ctx.hero)
    hero_sprite = ctx.hero.view()[0]
    hero_sprite.move((-bg_x, 128))
    sprites.append(hero_sprite)
