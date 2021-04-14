from contexts import Context
from comps.bar import Bar

import math
import pygame
from pygame import Rect, Surface
from config import tile_size
from assets import load as use_assets
from text import render as render_text
from filters import recolor, replace_color, outline
from anims.sine import SineAnim
import palette
import keyboard
from comps.skill import Skill


MARGIN = 8
OFFSET = 4
SPACING = 10

class SkillContext(Context):
  def __init__(ctx, parent, on_close=None):
    super().__init__(parent)
    ctx.on_close = on_close
    ctx.bar = Bar()
    ctx.options = [Skill(data=skill) for skill in ctx.parent.skills[ctx.parent.hero]]
    ctx.cursor_anim = SineAnim(15)
    ctx.enter()
    ctx.select_skill()

  def select_skill(ctx):
    game = ctx.parent
    hero = game.hero
    skill = hero.skill
    ctx.bar.print(get_skill_text(skill))

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
      ctx.handle_confirm()

    if key == pygame.K_TAB:
      ctx.handle_select()

    if key == pygame.K_ESCAPE or key == pygame.K_BACKSPACE:
      ctx.exit()

  def handle_turn(ctx, delta):
    game = ctx.parent
    hero = game.hero
    floor = game.floor
    hero_x, hero_y = hero.cell
    delta_x, delta_y = delta
    target_cell = (hero_x + delta_x, hero_y + delta_y)
    hero.face(delta)
    if ctx.bar.message != get_skill_text(hero.skill):
      ctx.select_skill()

  def handle_select(ctx, reverse=False):
    options = ctx.options
    game = ctx.parent
    hero = game.hero
    skills = game.skills[hero]
    skill = next((s for s in game.skills[hero] if s.name == hero.skill.name), None)
    index = skills.index(skill)
    next_skill = skills[(index + 1) % len(skills)]
    hero.skill = next_skill
    if hero.skill is not next_skill:
      ctx.select_skill()

  def handle_confirm(ctx):
    game = ctx.parent
    hero = game.hero
    if hero.skill.cost > game.sp:
      ctx.bar.print("You don't have enough SP!")
    else:
      ctx.exit(hero.skill)

  def enter(ctx):
    ctx.bar.enter()

  def exit(ctx, skill=None):
    ctx.bar.exit(on_end=lambda: ctx.close(skill))

  def draw(ctx, surface):
    assets = use_assets()
    game = ctx.parent
    hero = game.hero
    floor = game.floor
    skill = hero.skill
    camera = game.camera

    camera_x, camera_y = camera.pos
    facing_x, facing_y = hero.facing
    hero_x, hero_y = hero.cell
    cursor = (hero_x + facing_x, hero_y + facing_y)
    neighbors = []
    for r in range(1, skill.radius + 1):
      neighbors.extend([
        (hero_x, hero_y - r),
        (hero_x - r, hero_y),
        (hero_x + r, hero_y),
        (hero_x, hero_y + r)
      ])

    def scale_up(cell):
      col, row = cell
      x = col * tile_size - round(camera_x)
      y = row * tile_size - round(camera_y) + 1
      return (x, y)

    square = Surface((tile_size - 1, tile_size - 1), pygame.SRCALPHA)
    pygame.draw.rect(square, (*palette.RED, 0x7F), square.get_rect())
    for cell in neighbors:
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

    nodes = []
    sel_option = next((option for option in ctx.options if option.data.name == hero.skill.name), None)
    sel_index = ctx.options.index(sel_option)
    for i in range(len(ctx.options)):
      index = (sel_index + i) % len(ctx.options)
      option = ctx.options[index]
      sprite = option.render()
      if option.data.name != hero.skill.name:
        sprite = replace_color(sprite, (0xFF, 0xFF, 0xFF), (0x7F, 0x7F, 0x7F))
      x = MARGIN + i * SPACING
      y = surface.get_height()
      y += -MARGIN - ctx.bar.surface.get_height()
      y += -OFFSET - sprite.get_height()
      y += i * -SPACING
      nodes.append((sprite, x, y))

    nodes.reverse()
    for sprite, x, y in nodes:
      surface.blit(sprite, (x, y))

    title = render_text("SKILL", assets.fonts["smallcaps"])
    title = recolor(title, (0xFF, 0xFF, 0x00))
    title = outline(title, (0x00, 0x00, 0x00))
    surface.blit(title, (x + Skill.PADDING_X, y - title.get_height() + 4))

def get_skill_text(skill):
  return skill.desc + " (" + str(skill.cost) + " SP)"
