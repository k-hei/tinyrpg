import pygame
from contexts import Context
from town.sideview.actor import Actor
from cores.knight import KnightCore

class SideViewContext(Context):
  def __init__(ctx, hero=None):
    super().__init__()
    ctx.hero = Actor(core=hero or KnightCore())
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

  def draw(ctx, surface):
    hero_sprite = ctx.hero.view()
    hero_sprite.move((0, 128))
    hero_sprite.draw(surface)
