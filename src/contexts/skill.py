from contexts import Context
from comps.bar import Bar
import keyboard

import math
import pygame
from pygame import Rect, Surface
from config import tile_size
from assets import load as use_assets
from text import render as render_text
from filters import recolor, replace_color, outline
import palette
from comps.skill import Skill

from lerp import lerp
from easing.expo import ease_out
from anims.sine import SineAnim
from anims.tween import TweenAnim
from anims.flicker import FlickerAnim

MARGIN = 8
OFFSET = 4
SPACING = 10

class SkillContext(Context):
  def __init__(ctx, parent, on_close=None):
    super().__init__(parent)
    ctx.on_close = on_close
    ctx.bar = Bar()
    ctx.options = [Skill(data=skill) for skill in ctx.parent.skills[ctx.parent.hero]]
    ctx.offsets = {}
    ctx.cursor = None
    ctx.cursor_anim = SineAnim(60)
    ctx.anims = []
    ctx.exiting = False
    ctx.confirmed = False
    ctx.enter()
    ctx.select_skill()

  def select_skill(ctx, skill=None):
    if skill is None:
      game = ctx.parent
      hero = game.hero
      skill = hero.skill
    ctx.bar.print(get_skill_text(skill))

  def handle_keydown(ctx, key):
    if len(ctx.anims):
      return

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
    old_skill = hero.skill
    new_skill = skills[(index + 1) % len(skills)]
    if old_skill.name != new_skill.name:
      ctx.select_skill(new_skill)
      ctx.anims.append(TweenAnim(duration=12, target=options))
    hero.skill = new_skill

  def handle_confirm(ctx):
    game = ctx.parent
    hero = game.hero
    if hero.skill.cost > game.sp:
      ctx.bar.print("You don't have enough SP!")
    else:
      ctx.exit(hero.skill)

  def enter(ctx):
    ctx.bar.enter()
    index = 0
    for option in ctx.options:
      ctx.anims.append(TweenAnim(
        duration=10,
        delay=8 * index,
        target=index
      ))
      index += 1

  def exit(ctx, skill=None):
    ctx.exiting = True
    index = 0
    for option in ctx.options:
      is_last = skill is None and index == len(ctx.options) - 1
      ctx.anims.append(TweenAnim(
        duration=6,
        target=index,
        on_end=ctx.close() if is_last else None
      ))
      index += 1
    if skill:
      ctx.confirmed = True
      ctx.bar.exit()
      ctx.anims.append(FlickerAnim(
        duration=30,
        target="cursor",
        on_end=lambda: ctx.close(skill)
      ))
    else:
      ctx.bar.exit()

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

    for anim in ctx.anims:
      anim.update()
      if anim.done:
        ctx.anims.remove(anim)

    anim = ctx.anims[0] if ctx.anims else None
    cursor_anim = ctx.cursor_anim
    t = cursor_anim.update()
    if not ctx.exiting and not (anim and anim.target == "cursor"):
      if cursor_anim.time % 60 >= 40:
        alpha = 0x7f
      elif cursor_anim.time % 60 >= 20:
        alpha = 0x6f
      else:
        alpha = 0x5f
      square = Surface((tile_size - 1, tile_size - 1), pygame.SRCALPHA)
      pygame.draw.rect(square, (*palette.RED, alpha), square.get_rect())
      for cell in neighbors:
        x, y = scale_up(cell)
        surface.blit(square, (x, y))

    if ctx.cursor:
      cursor_x, cursor_y, cursor_scale = ctx.cursor
    else:
      cursor_x, cursor_y = scale_up(hero.cell)
      cursor_scale = 0.5

    if anim and anim.target == "cursor":
      if anim.visible:
        cursor_sprite = assets.sprites["cursor_cell1"]
      else:
        cursor_sprite = None
      if anim.done:
        ctx.anims.remove(anim)
    else:
      t = min(2, math.floor((t + 1) / 2 * 3))
      cursor_sprite = assets.sprites["cursor_cell"]
      if t == 1:
        cursor_sprite = assets.sprites["cursor_cell1"]
      elif t == 2:
        cursor_sprite = assets.sprites["cursor_cell2"]

    new_cursor_x, new_cursor_y = scale_up(cursor)
    if ctx.exiting and not ctx.confirmed:
      new_cursor_x, new_cursor_y = scale_up(hero.cell)
      cursor_scale += -cursor_scale / 4
    else:
      cursor_scale += (1 - cursor_scale) / 4
    cursor_x += (new_cursor_x - cursor_x) / 4
    cursor_y += (new_cursor_y - cursor_y) / 4

    if cursor_sprite:
      cursor_sprite = pygame.transform.scale(cursor_sprite, (
        int(cursor_sprite.get_width() * cursor_scale),
        int(cursor_sprite.get_height() * cursor_scale)
      ))
      surface.blit(cursor_sprite, (
        cursor_x + tile_size // 2 - cursor_sprite.get_width() // 2 - 1,
        cursor_y + tile_size // 2 - cursor_sprite.get_height() // 2 - 1
      ))
    ctx.cursor = (cursor_x, cursor_y, cursor_scale)

    ctx.bar.draw(surface)

    nodes = []
    sel_option = next((option for option in ctx.options if option.data.name == hero.skill.name), None)
    sel_index = ctx.options.index(sel_option)

    def get_skill_pos(sprite, i):
      x = MARGIN + i * SPACING
      y = surface.get_height()
      y += -MARGIN - ctx.bar.surface.get_height()
      y += -OFFSET - sprite.get_height()
      y += i * -SPACING
      return (x, y)

    options = ctx.options
    for i in range(len(options)):
      index = (sel_index + i) % len(options)
      option = options[index]
      sprite = option.render()
      height = sprite.get_height()
      if option.data.name != hero.skill.name:
        sprite = replace_color(sprite, palette.WHITE, palette.GRAY)
      x, y = get_skill_pos(sprite, i)

      anim = ctx.anims[0] if ctx.anims else None
      if anim and anim.target is options:
        old_i = (i + 1) % len(options)
        old_x, old_y = get_skill_pos(sprite, old_i)
        new_x, new_y = get_skill_pos(sprite, i)
        t = ease_out(anim.time / anim.duration)
        if anim.done:
          ctx.anims.remove(anim)
        x = lerp(old_x, new_x, t)
        y = lerp(old_y, new_y, t)
        if option.data.name == hero.skill.name:
          value = lerp(0x7F, 0xFF, t)
          sprite = replace_color(sprite, palette.WHITE, (value, value, value))

      anim = next((anim for anim in ctx.anims if anim.target == i), None)
      if anim:
        sprite = assets.sprites["skill"]
        sprite = replace_color(sprite, palette.WHITE, palette.GRAY)
        t = max(0, anim.time / anim.duration)
        if ctx.exiting:
          t = 1 - t
        else:
          t = ease_out(t)
        if anim.done:
          ctx.anims.remove(anim)
        height = int(height * t)
      elif ctx.exiting:
        sprite = None

      if sprite:
        nodes.append((sprite, x, y, height))

    nodes.reverse()
    for sprite, x, y, height in nodes:
      real_height = sprite.get_height()
      sprite = pygame.transform.scale(sprite, (sprite.get_width(), height))
      surface.blit(sprite, (x, y + real_height / 2 - sprite.get_height() / 2))

    first_anim = next((anim for anim in ctx.anims if anim.target == 0), None)
    if not ctx.exiting and not first_anim:
      title = render_text("SKILL", assets.fonts["smallcaps"])
      title = recolor(title, (0xFF, 0xFF, 0x00))
      title = outline(title, (0x00, 0x00, 0x00))
      x = MARGIN + Skill.PADDING_X - 4
      y = surface.get_height()
      y += -MARGIN - ctx.bar.surface.get_height()
      y += -OFFSET - assets.sprites["skill"].get_height()
      y += -title.get_height() + 4
      surface.blit(title, (x, y))

def get_skill_text(skill):
  return skill.name + ': ' + skill.desc + " (" + str(skill.cost) + " SP)"
