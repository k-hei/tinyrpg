from contexts import Context
from comps.bar import Bar
import keyboard

import math
import pygame
from pygame import Rect, Surface
from config import TILE_SIZE
from assets import load as use_assets
from text import render as render_text
from filters import recolor, replace_color, outline
import palette
from comps.skill import Skill

from lib.lerp import lerp
from easing.expo import ease_out
from anims.sine import SineAnim
from anims.tween import TweenAnim
from anims.flicker import FlickerAnim

from dungeon.actors import DungeonActor
from lib.cell import manhattan

MARGIN = 8
OFFSET = 4
SPACING = 10

class SkillContext(Context):
  def __init__(ctx, parent, actor, skill_selected, on_close=None):
    super().__init__(parent)
    ctx.actor = actor
    ctx.skill = skill_selected
    ctx.on_close = on_close
    ctx.bar = Bar()
    ctx.options = actor.get_active_skills()
    ctx.offsets = {}
    ctx.cursor = None
    ctx.cursor_anim = SineAnim(60)
    ctx.anims = []
    ctx.exiting = False
    ctx.confirmed = False
    ctx.enter()
    ctx.print_skill(skill_selected)
    enemy = parent.find_closest_visible_enemy(actor)
    if enemy:
      actor.face(enemy.cell)

  def print_skill(ctx, skill=None):
    if skill:
      ctx.bar.print(skill().text())
    else:
      ctx.bar.print("No active skills equipped.")

  def handle_keydown(ctx, key):
    if len(ctx.anims):
      return

    if keyboard.get_pressed(key) != 1:
      return

    key_deltas = {
      pygame.K_LEFT: (-1, 0),
      pygame.K_RIGHT: (1, 0),
      pygame.K_UP: (0, -1),
      pygame.K_DOWN: (0, 1),
      pygame.K_a: (-1, 0),
      pygame.K_d: (1, 0),
      pygame.K_w: (0, -1),
      pygame.K_s: (0, 1)
    }
    if key in key_deltas:
      delta = key_deltas[key]
      ctx.handle_turn(delta)

    if key == pygame.K_RETURN or key == pygame.K_SPACE:
      ctx.handle_confirm()

    if key == pygame.K_TAB:
      ctx.handle_select()

    if key == pygame.K_ESCAPE or key == pygame.K_BACKSPACE:
      ctx.exit()

  def handle_turn(ctx, delta):
    game = ctx.parent
    hero = ctx.actor
    floor = game.floor
    skill = game.skill
    hero_x, hero_y = hero.cell
    delta_x, delta_y = delta
    target_cell = (hero_x + delta_x, hero_y + delta_y)
    hero.facing = delta
    if ctx.bar.message != skill().text():
      ctx.print_skill()

  def handle_select(ctx, reverse=False):
    options = ctx.options
    game = ctx.parent
    hero = game.hero
    skills = [s for s in hero.skills if s.kind != "passive"]
    old_skill = game.skill
    if old_skill is None:
      return
    index = skills.index(old_skill)
    new_skill = skills[(index + 1) % len(skills)]
    if old_skill != new_skill:
      ctx.print_skill(new_skill)
      ctx.anims.append(TweenAnim(duration=12, target=options))
    game.skill = new_skill

  def handle_confirm(ctx):
    game = ctx.parent
    skill = game.skill
    if skill is None:
      return
    if skill.cost > game.parent.sp:
      ctx.bar.print("You don't have enough SP!")
    else:
      ctx.exit(skill)

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
    def close():
      ctx.parent.camera.blur()
      ctx.close(skill)

    ctx.exiting = True
    index = 0
    for option in ctx.options:
      is_last = skill is None and index == len(ctx.options) - 1
      ctx.anims.append(TweenAnim(
        duration=6,
        target=index,
        on_end=close if is_last else None
      ))
      index += 1
    if len(ctx.options) == 0:
      ctx.bar.exit(on_end=close)
    elif skill:
      ctx.confirmed = True
      ctx.bar.exit()
      ctx.anims.append(FlickerAnim(
        duration=30,
        target="cursor",
        on_end=close
      ))
    else:
      ctx.bar.exit()

  def draw(ctx, surface):
    assets = use_assets()
    game = ctx.parent
    hero = game.hero
    floor = game.floor
    camera = game.camera
    skill = game.skill

    camera_x, camera_y = camera.pos
    facing_x, facing_y = hero.facing
    hero_x, hero_y = hero.cell
    neighbors, cursor = find_skill_targets(skill, hero, floor)

    if cursor not in neighbors:
      cursor = neighbors[0]

    camera_speed = 8
    if skill and skill.range_max == math.inf:
      camera.focus(cursor, 16)
    else:
      camera.focus(cursor, 8)

    def scale_up(cell):
      col, row = cell
      x = col * TILE_SIZE - round(camera_x)
      y = row * TILE_SIZE - round(camera_y) + 1
      return x, y

    for anim in ctx.anims:
      anim.update()
      if anim.done:
        ctx.anims.remove(anim)

    anim = ctx.anims[0] if ctx.anims else None
    cursor_anim = ctx.cursor_anim
    t = cursor_anim.update()
    if skill and not ctx.exiting and not (anim and anim.target == "cursor"):
      if cursor_anim.time % 60 >= 40:
        alpha = 0x7f
      elif cursor_anim.time % 60 >= 20:
        alpha = 0x6f
      else:
        alpha = 0x5f
      square = Surface((TILE_SIZE - 1, TILE_SIZE - 1), pygame.SRCALPHA)
      color = skill.color
      pygame.draw.rect(square, (*color, alpha), square.get_rect())
      for cell in neighbors:
        x, y = scale_up(cell)
        surface.blit(square, (x, y))

    if ctx.cursor:
      cursor_col, cursor_row, cursor_scale = ctx.cursor
    else:
      cursor_col, cursor_row = hero.cell
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

    new_cursor_col, new_cursor_row = cursor
    if ctx.exiting and not ctx.confirmed:
      new_cursor_col, new_cursor_row = hero.cell
      cursor_scale += -cursor_scale / 4
    else:
      cursor_scale += (1 - cursor_scale) / 4
    cursor_col += (new_cursor_col - cursor_col) / 4
    cursor_row += (new_cursor_row - cursor_row) / 4
    cursor_x, cursor_y = scale_up((cursor_col, cursor_row))

    if cursor_sprite:
      cursor_sprite = pygame.transform.scale(cursor_sprite, (
        int(cursor_sprite.get_width() * cursor_scale),
        int(cursor_sprite.get_height() * cursor_scale)
      ))
      surface.blit(cursor_sprite, (
        cursor_x + TILE_SIZE // 2 - cursor_sprite.get_width() // 2 - 1,
        cursor_y + TILE_SIZE // 2 - cursor_sprite.get_height() // 2 - 1
      ))
    ctx.cursor = (cursor_col, cursor_row, cursor_scale)

    ctx.bar.draw(surface)

    nodes = []
    sel_option = next((option for option in ctx.options if option is skill), None)
    sel_index = ctx.options.index(sel_option) if sel_option in ctx.options else 0

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
      if skill:
        sprite = Skill.render(skill=option, selected=option is skill)
      else:
        sprite = assets.sprites["skill"].copy()
        text = render_text("[ N/A ]", assets.fonts["smallcaps"])
        text = recolor(text, palette.WHITE)
        sprite.blit(text, (
          sprite.get_width() // 2 - text.get_width() // 2,
          sprite.get_height() // 2 - text.get_height() // 2 - 1
        ))
      height = sprite.get_height()
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
        if option is skill:
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
      x = MARGIN + Skill.PADDING_X
      y = surface.get_height()
      y += -MARGIN - ctx.bar.surface.get_height()
      y += -OFFSET - assets.sprites["skill"].get_height()
      y += -title.get_height() + 3
      surface.blit(title, (x, y))

def find_skill_targets(skill, user, floor):
  targets = []
  user_x, user_y = user.cell
  facing_x, facing_y = user.facing
  cursor = (user_x + facing_x, user_y + facing_y)
  if skill.range_type == "radial" or skill.range_type == "linear" and skill.range_max == 1:
    if skill.range_min == 0:
      targets.append((user_x, user_y))
    targets.extend([
      (user_x, user_y - 1),
      (user_x - 1, user_y),
      (user_x + 1, user_y),
      (user_x, user_y + 1)
    ])
  elif skill.range_type == "linear" and skill.range_max > 2:
    targets.append(cursor)
    is_blocked = False
    r = 1
    while not is_blocked and r < skill.range_max:
      if floor.get_tile_at(cursor).solid or floor.get_elem_at(cursor):
        is_blocked = True
      else:
        cursor_x, cursor_y = cursor
        cursor = (cursor_x + facing_x, cursor_y + facing_y)
        targets.append(cursor)
      r += 1
  elif skill.range_type == "linear":
    for r in range(skill.range_min, skill.range_max + 1):
      targets.append((user_x + facing_x * r, user_y + facing_y * r))
  return targets, cursor
