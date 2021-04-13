from contexts import Context
from comps.bar import Bar

import math
import pygame
from pygame import Rect, Surface
from config import tile_size
from assets import load as use_assets
from anims.sine import SineAnim
import palette

import keyboard

class SkillContext(Context):
  def __init__(ctx, parent, on_close=None):
    super().__init__(parent)
    ctx.on_close = on_close
    ctx.bar = Bar()
    ctx.cursor_anim = SineAnim(15)
    ctx.enter()
    ctx.select_skill()

  def select_skill(ctx):
    game = ctx.parent
    hero = game.hero
    skill = hero.skill
    ctx.bar.print(skill.name + ": " + skill.desc)

  def handle_keydown(ctx, key):
    if keyboard.get_pressed(key) != 1:
      return

    key_deltas = {
      pygame.K_LEFT: (-1, 0),
      pygame.K_RIGHT: (1, 0),
      pygame.K_UP: (0, -1),
      pygame.K_DOWN: (0, 1)
    }
    if key in key_deltas:
      delta = key_deltas[key]
      ctx.handle_turn(delta)

    if key == pygame.K_RETURN:
      ctx.exit()

  def handle_turn(ctx, delta):
    game = ctx.parent
    hero = game.hero
    floor = game.floor
    hero_x, hero_y = hero.cell
    delta_x, delta_y = delta
    target_cell = (hero_x + delta_x, hero_y + delta_y)
    if floor.is_cell_empty(target_cell, hero):
      hero.face(delta)

  def enter(ctx):
    ctx.bar.enter()

  def exit(ctx):
    ctx.bar.exit(on_end=ctx.close)

  def draw(ctx, surface):
    assets = use_assets()
    game = ctx.parent # may not always be true
    hero = game.hero
    floor = game.floor
    camera_x, camera_y = game.camera.pos
    facing_x, facing_y = hero.facing
    hero_x, hero_y = hero.cell
    cursor = (hero_x + facing_x, hero_y + facing_y)
    neighbors = [
      (hero_x, hero_y - 1),
      (hero_x - 1, hero_y),
      (hero_x + 1, hero_y),
      (hero_x, hero_y + 1)
    ]

    if not floor.is_cell_empty(cursor, hero):
      cursor = next((n for n in neighbors if floor.is_cell_empty(n, hero)), None)
      if cursor:
        cursor_x, cursor_y = cursor
        facing = (cursor_x - hero_x, cursor_y - hero_y)
        hero.face(facing)

    def scale_up(cell):
      col, row = cell
      x = col * tile_size - round(camera_x)
      y = row * tile_size - round(camera_y) + 1
      return (x, y)

    square = Surface((tile_size - 1, tile_size - 1), pygame.SRCALPHA)
    pygame.draw.rect(square, (*palette.RED, 0x7F), square.get_rect())
    for cell in neighbors:
      if not floor.is_cell_empty(cell, hero):
        continue
      x, y = scale_up(cell)
      surface.blit(square, (x, y))

    if cursor:
      t = math.floor((ctx.cursor_anim.update() + 1) / 2 * 3)
      cursor_sprite = assets.sprites["cursor_cell"]
      if t == 1:
        cursor_sprite = assets.sprites["cursor_cell1"]
      elif t == 2:
        cursor_sprite = assets.sprites["cursor_cell2"]
      cursor_x, cursor_y = scale_up(cursor)
      surface.blit(cursor_sprite, (cursor_x - 1 - t, cursor_y - 1 - t))

    ctx.bar.draw(surface)
