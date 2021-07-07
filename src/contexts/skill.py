from contexts import Context
from comps.bar import Bar
import keyboard

import math
import pygame
from pygame import Rect, Surface
from config import TILE_SIZE, WINDOW_HEIGHT
from assets import load as use_assets
from text import render as render_text
from filters import recolor, replace_color, outline
from palette import BLACK, WHITE, GRAY, YELLOW
from comps.skill import Skill
from sprite import Sprite

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

def find_closest_cell_in_range(range_cells, target_cell):
  if not range_cells:
    return None
  # TODO: take delta into account during sort
  return sorted(range_cells, key=lambda c: manhattan(c, target_cell))[0]

class SkillContext(Context):
  def __init__(ctx, skills, selected_skill=None, actor=None, on_close=None):
    super().__init__()
    ctx.skills = skills or actor.get_active_skills()
    ctx.skill = selected_skill or skills and skills[0] or None
    ctx.skill_range = None
    ctx.actor = actor
    ctx.on_close = on_close
    ctx.bar = Bar()
    ctx.offsets = {}
    ctx.dest = None
    ctx.cursor = None
    ctx.cursor_anim = SineAnim(60)
    ctx.anims = []
    ctx.exiting = False
    ctx.confirmed = False

  def init(ctx):
    if not ctx.actor:
      return
    ctx.skill_range = ctx.skill().find_range(ctx.actor, ctx.parent.floor)
    enemy = ctx.parent.find_closest_visible_enemy(ctx.actor)
    if enemy:
      ctx.actor.face(enemy.cell)
      ctx.dest = find_closest_cell_in_range(ctx.skill_range, enemy.cell)

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

    if key in keyboard.ARROW_DELTAS:
      delta = keyboard.ARROW_DELTAS[key]
      return ctx.handle_direction(delta)

    if key == pygame.K_RETURN or key == pygame.K_SPACE:
      return ctx.handle_confirm()

    if key == pygame.K_TAB:
      return ctx.handle_select()

    if key == pygame.K_ESCAPE or key == pygame.K_BACKSPACE:
      return ctx.exit()

  def handle_direction(ctx, delta):
    if ctx.skill and ctx.skill.range_type == "radial" and ctx.skill.range_max > 1:
      ctx.handle_move(delta)
    else:
      ctx.handle_turn(delta)

  def handle_move(ctx, delta):
    if ctx.dest is None:
      return False
    cursor_x, cursor_y = ctx.dest
    delta_x, delta_y = delta
    ctx.dest = find_closest_cell_in_range(ctx.skill_range, target_cell=(cursor_x + delta_x, cursor_y + delta_y))
    ctx.actor.face(ctx.dest)

  def handle_turn(ctx, delta):
    game = ctx.parent
    hero = ctx.actor
    if hero:
      hero_x, hero_y = hero.cell
      delta_x, delta_y = delta
      target_cell = (hero_x + delta_x, hero_y + delta_y)
      hero.facing = delta
    skill = ctx.skill
    if skill and ctx.bar.message != skill().text():
      ctx.print_skill()

  def handle_select(ctx, reverse=False):
    options = ctx.skills
    game = ctx.parent
    skills = ctx.skills
    old_skill = ctx.skill
    if old_skill is None:
      return
    index = skills.index(old_skill)
    new_skill = skills[(index + 1) % len(skills)]
    if old_skill != new_skill:
      ctx.print_skill(new_skill)
      ctx.anims.append(TweenAnim(duration=12, target=options))
    ctx.skill = new_skill

  def handle_confirm(ctx):
    game = ctx.parent
    skill = ctx.skill
    dest = ctx.dest
    if skill is None:
      return
    if game.parent and skill.cost > game.parent.sp:
      ctx.bar.print("You don't have enough SP!")
    else:
      ctx.exit(skill, dest)

  def enter(ctx):
    ctx.bar.enter()
    index = 0
    for option in ctx.skills:
      ctx.anims.append(TweenAnim(
        duration=10,
        delay=8 * index,
        target=index
      ))
      index += 1
    ctx.print_skill(ctx.skill)

  def exit(ctx, skill=None, dest=None):
    def close():
      if "camera" in dir(ctx.parent):
        ctx.parent.camera.blur()
        ctx.parent.child = None
      if ctx.on_close:
        ctx.on_close(skill, dest)

    ctx.exiting = True
    index = 0
    for option in ctx.skills:
      is_last = skill is None and index == len(ctx.skills) - 1
      ctx.anims.append(TweenAnim(
        duration=6,
        target=index,
        on_end=close if is_last else None
      ))
      index += 1
    if len(ctx.skills) == 0:
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

  def update(ctx):
    for anim in ctx.anims:
      if anim.done:
        ctx.anims.remove(anim)
      else:
        anim.update()

  def view(ctx):
    sprites = []
    assets = use_assets()
    hero = ctx.actor
    skill = ctx.skill
    cursor = ctx.dest
    if hero:
      game = ctx.parent
      floor = game.floor
      camera = game.camera
      camera_x, camera_y = camera.pos
      facing_x, facing_y = hero.facing
      hero_x, hero_y = hero.cell

      skill_targets = skill().find_targets(hero, floor, dest=ctx.dest)
      if (skill.range_type == "row"
      or skill.range_type == "linear" and skill.range_max > 1):
        skill_range = skill_targets
      else:
        skill_range = skill().find_range(hero, floor)

      # if skill.range_type == "linear" and skill.range_max > 1:
      #   cursor = skill_range[-1] if skill_range else None
      # if not cursor:
      #   cursor = (hero_x + facing_x, hero_y + facing_y)

      # if cursor not in skill_range:
      #   if skill_range:
      #     def dist(cell):
      #       cell_x, cell_y = cell
      #       cursor_x, cursor_y = cursor
      #       dist_x = abs(cell_x - hero_x) + abs(cell_x - cursor_x)
      #       dist_y = abs(cell_y - hero_y) + abs(cell_y - cursor_y)
      #       offset = -1 if dist_x == 0 or dist_y == 0 else 0
      #       return dist_x + dist_y + offset
      #     cursor = sorted(skill_range, key=dist)[0]
      #   else:
      #     cursor = hero.cell
      ctx.dest = cursor

      camera_speed = 8
      if skill and skill.range_max == math.inf:
        camera.focus(cursor, speed=16, force=True)
      else:
        camera.focus(cursor, speed=8, force=True)

      def scale_up(cell):
        col, row = cell
        x = col * TILE_SIZE - round(camera_x)
        y = row * TILE_SIZE - round(camera_y) + 1
        return x, y

    if cursor:
      anim = ctx.anims[0] if ctx.anims else None
      cursor_anim = ctx.cursor_anim
      t = cursor_anim.update()
      if skill and not ctx.exiting and not (anim and anim.target == "cursor"):
        alpha = [0x5f, 0x6f, 0x7f][int(cursor_anim.time % 60 / 60 * 3)]
        square_lo = Surface((TILE_SIZE - 1, TILE_SIZE - 1), pygame.SRCALPHA)
        square_hi = Surface((TILE_SIZE - 1, TILE_SIZE - 1), pygame.SRCALPHA)
        pygame.draw.rect(square_lo, skill.color & 0xFFFFFF | int(alpha) << 24, square_lo.get_rect())
        pygame.draw.rect(square_hi, skill.color & 0xFFFFFF | int(alpha + 0x5f) << 24, square_hi.get_rect())
        square_cells = list(set(skill_range + skill_targets))
        for cell in square_cells:
          x, y = scale_up(cell)
          square_image = square_hi if cell in skill_targets else square_lo
          sprites.append(Sprite(
            image=square_image,
            pos=(x, y)
          ))

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
        sprites.append(Sprite(
          image=cursor_sprite,
          pos=(
            cursor_x + TILE_SIZE // 2 - cursor_sprite.get_width() // 2 - 1,
            cursor_y + TILE_SIZE // 2 - cursor_sprite.get_height() // 2 - 1
          ),
          layer="ui"
        ))
        ctx.cursor = (cursor_col, cursor_row, cursor_scale)

    sprites += ctx.bar.view()
    nodes = []
    sel_option = next((option for option in ctx.skills if option is skill), None)
    sel_index = ctx.skills.index(sel_option) if sel_option in ctx.skills else 0

    def get_skill_pos(sprite, i):
      x = MARGIN + i * SPACING
      y = WINDOW_HEIGHT
      y += -MARGIN - ctx.bar.surface.get_height()
      y += -OFFSET - sprite.get_height()
      y += i * -SPACING
      return (x, y)

    options = ctx.skills
    for i in range(len(options)):
      index = (sel_index + i) % len(options)
      option = options[index]
      if skill:
        sprite = Skill.render(skill=option, selected=option is skill)
      else:
        sprite = assets.sprites["skill"].copy()
        text = render_text("[ N/A ]", assets.fonts["smallcaps"])
        text = recolor(text, WHITE)
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
          sprite = replace_color(sprite, WHITE, (value, value, value))

      anim = next((anim for anim in ctx.anims if anim.target == i), None)
      if anim:
        sprite = assets.sprites["skill"]
        sprite = replace_color(sprite, WHITE, GRAY)
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
      sprites.append(Sprite(
        image=sprite,
        pos=(x, y + real_height / 2 - sprite.get_height() / 2),
        layer="hud"
      ))

    first_anim = next((anim for anim in ctx.anims if anim.target == 0), None)
    if not ctx.exiting and not first_anim:
      title = render_text("SKILL", assets.fonts["smallcaps"])
      title = recolor(title, YELLOW)
      title = outline(title, BLACK)
      x = MARGIN + Skill.PADDING_X
      y = WINDOW_HEIGHT
      y += -MARGIN - ctx.bar.surface.get_height()
      y += -OFFSET - assets.sprites["skill"].get_height()
      y += -title.get_height() + 3
      sprites.append(Sprite(
        image=title,
        pos=(x, y),
        layer="hud"
      ))

    return sprites
