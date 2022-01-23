import math
import pygame
from pygame import Rect, Surface, Color
from pygame.transform import flip
import lib.keyboard as keyboard
import lib.gamepad as gamepad
import lib.input as input
from lib.cell import manhattan
from lib.lerp import lerp
import lib.vector as vector
from easing.expo import ease_out

from assets import load as use_assets
from text import render as render_text
from lib.filters import recolor, replace_color, outline
from colors.palette import BLACK, WHITE, GRAY, GOLD
from config import TILE_SIZE, WINDOW_HEIGHT

from contexts import Context
from comps.bar import Bar
from comps.skill import Skill
from lib.sprite import Sprite

from anims.sine import SineAnim
from anims.tween import TweenAnim
from anims.flicker import FlickerAnim

from dungeon.actors import DungeonActor

MARGIN = 8
OFFSET = 4
SPACING = 10

def find_closest_cell_in_range(range_cells, target_cell, delta=None):
  if not range_cells:
    return None
  if delta:
    target_cell = vector.add(target_cell, tuple([x / 10 for x in delta]))
  return sorted(range_cells, key=lambda c: manhattan(c, target_cell))[0]

class NextAnim(TweenAnim): pass
class PrevAnim(TweenAnim): pass

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
    ctx.cache_camera_pos = None
    ctx.cache_camera_targets = []

  def init(ctx):
    if not ctx.actor:
      return
    hero = ctx.actor
    stage = ctx.parent.stage
    skill = ctx.skill
    enemy = ctx.parent.find_closest_enemy(hero, elems=[e for c in hero.visible_cells for e in stage.get_elems_at(c)])
    if enemy:
      hero.face(enemy.cell)
      target_cell = enemy.cell
    else:
      hero_x, hero_y = hero.cell
      facing_x, facing_y = hero.facing
      target_cell = (hero_x + facing_x, hero_y + facing_y)
    if not skill:
      ctx.dest = hero.cell
      return
    ctx.skill_range = skill().find_range(hero, stage)
    if skill.range_type == "linear" and skill.range_max > 1:
      ctx.dest = ctx.skill_range[-1]
    else:
      ctx.dest = find_closest_cell_in_range(ctx.skill_range, target_cell, delta=hero.facing)
    ctx.cache_camera_targets = ctx.parent.camera.target_groups.copy()

  def close(ctx, *args):
    ctx.parent.camera.target_groups = ctx.cache_camera_targets
    super().close(*(args or [None, None]))

  def print_skill(ctx, skill=None):
    if skill:
      ctx.bar.print(skill().text())
    else:
      ctx.bar.print("No active skills equipped.")

  def handle_press(ctx, button):
    if len(ctx.anims):
      return

    if not button or input.get_state(button) > 1:
      return

    delta = input.resolve_delta(button, fixed_axis=True)
    if delta != (0, 0):
      return ctx.handle_direction(delta)

    control = input.resolve_control(button)
    button = input.resolve_button(button)

    if button == input.BUTTON_L:
      return ctx.handle_select()

    if button == input.BUTTON_R:
      return ctx.handle_select(reverse=True)

    if control == input.CONTROL_CONFIRM:
      return ctx.handle_confirm()

    if control == input.CONTROL_CANCEL:
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
    ctx.dest = find_closest_cell_in_range(ctx.skill_range, target_cell=(cursor_x + delta_x, cursor_y + delta_y), delta=delta)
    ctx.actor.face(ctx.dest)

  def handle_turn(ctx, delta):
    game = ctx.parent
    stage = game.stage
    hero = ctx.actor
    if hero:
      hero_x, hero_y = hero.cell
      delta_x, delta_y = delta
      target_cell = (hero_x + delta_x, hero_y + delta_y)
      hero.facing = delta
    skill = ctx.skill
    if skill and ctx.bar.message != skill().text():
      ctx.print_skill()

    ctx.dest = None
    if hero and skill:
      ctx.skill_range = skill().find_range(hero, stage)
      if ctx.skill_range:
        get_enemies_at_cell = lambda c: (e for e in stage.get_elems_at(c) if isinstance(e, DungeonActor) and not e.allied(hero))
        enemy_cells = [c for c in ctx.skill_range if next(get_enemies_at_cell(c), None)]
        enemy_cell = enemy_cells and sorted(enemy_cells, key=lambda c: manhattan(c, hero.cell))[0]
        if enemy_cell and enemy_cell in ctx.skill_range:
          ctx.dest = enemy_cell
        elif skill.range_min == 1 and skill.range_max == 1:
          ctx.dest = target_cell
        else:
          ctx.dest = ctx.skill_range[-1]

    if hero and not ctx.dest:
      ctx.dest = hero.cell

  def handle_select(ctx, reverse=False):
    options = ctx.skills
    game = ctx.parent
    hero = ctx.actor
    skills = ctx.skills
    old_skill = ctx.skill
    if old_skill is None:
      return
    old_index = skills.index(old_skill)
    if reverse:
      new_index = old_index - 1
      if new_index < 0:
        new_index += len(skills)
    else:
      new_index = (old_index + 1) % len(skills)
    new_skill = skills[new_index]
    if old_skill != new_skill:
      ctx.print_skill(new_skill)
      ctx.anims.append((PrevAnim if reverse else NextAnim)(duration=12, target=options))
      ctx.skill_range = new_skill().find_range(ctx.actor, game.stage)
      pivot_cell = vector.add(hero.cell, tuple([x / 10 for x in hero.facing]))
      ctx.dest = (sorted(ctx.skill_range, key=lambda c: manhattan(c, pivot_cell))[0]
        if ctx.skill_range
        else hero.cell)
    ctx.skill = new_skill

  def handle_confirm(ctx):
    game = ctx.parent
    skill = ctx.skill
    dest = ctx.dest
    if skill is None:
      return
    if skill.cost > game.store.sp:
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
    ctx.exiting = True
    index = 0
    close = lambda: ctx.close(skill, dest)
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
      stage = game.stage
      camera = game.camera
      skill_targets = skill().find_targets(hero, stage, dest=ctx.dest) if skill else []
      skill_range = skill().find_range(hero, stage) if skill else []
      ctx.dest = cursor

      camera_pos = vector.scale(
        vector.add(cursor, (0.5, 0.5)),
        TILE_SIZE
      )
      camera.focus(camera_pos, force=True)

      def scale_up(cell):
        return vector.add(
          vector.subtract(
            vector.scale(cell, TILE_SIZE),
            camera.pos
          ),
          vector.scale(camera.size, 0.5),
          (1, 1),
        )

    if cursor:
      anim = ctx.anims[0] if ctx.anims else None
      cursor_anim = ctx.cursor_anim
      t = cursor_anim.update()
      if skill and not ctx.exiting and not (anim and anim.target == "cursor"):
        alpha = [0x5f, 0x6f, 0x7f][int(cursor_anim.time % 60 / 60 * 3)]
        square_lo = Surface((TILE_SIZE - 1, TILE_SIZE - 1), pygame.SRCALPHA)
        square_hi = Surface((TILE_SIZE - 1, TILE_SIZE - 1), pygame.SRCALPHA)
        pygame.draw.rect(square_lo, Color(*skill.color, alpha), square_lo.get_rect())
        pygame.draw.rect(square_hi, Color(*skill.color, alpha + 0x5f), square_hi.get_rect())
        square_cells = list(set(skill_range + skill_targets))
        for cell in square_cells:
          tile = stage.get_tile_at(cell)
          z = tile.elev if tile else 0
          x, y = cell
          y -= z
          x, y = scale_up((x, y))
          square_image = square_hi if cell in skill_targets else square_lo
          if z != int(z):
            slope_image = assets.sprites["square_hslope"]
            if tile.direction == (1, 0):
              slope_image = flip(slope_image, True, False)
            elif tile.direction == (0, -1):
              slope_image = assets.sprites["square_vslope"]
            square_image = Surface(slope_image.get_size(), pygame.SRCALPHA)
            square_image.blit(slope_image, (0, 0))
            square_color = Color(*skill.color, alpha + (cell in skill_targets and 0x5f or 0))
            square_image = replace_color(square_image, WHITE, square_color)
            y -= TILE_SIZE // 2
          sprites.append(Sprite(
            image=square_image,
            pos=(x, y + square_image.get_height()),
            origin=("left", "bottom"),
            layer="elems",
            offset=z * TILE_SIZE
          ))

      if ctx.cursor:
        cursor_col, cursor_row, cursor_scale = ctx.cursor
      else:
        cursor_col, cursor_row = hero.cell
        cursor_scale = 0.5

      if anim and anim.target == "cursor":
        if anim.visible:
          cursor_sprite = assets.sprites["cursor_cell"][1]
        else:
          cursor_sprite = None
        if anim.done:
          ctx.anims.remove(anim)
      else:
        t = min(2, math.floor((t + 1) / 2 * 3))
        cursor_sprite = assets.sprites["cursor_cell"][t]

      new_cursor_col, new_cursor_row = cursor
      cursor_tile = stage.get_tile_at(cursor)
      cursor_z = cursor_tile.elev if cursor_tile else 0
      new_cursor_row -= cursor_z
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
        if type(anim) is NextAnim:
          old_i = (i + 1) % len(options)
        else:
          old_i = i - 1
          if old_i < 0:
            old_i += len(options)
        old_x, old_y = get_skill_pos(sprite, old_i)
        new_x, new_y = get_skill_pos(sprite, i)
        t = ease_out(anim.time / anim.duration)
        if anim.done:
          ctx.anims.remove(anim)
        x = lerp(old_x, new_x, t)
        y = lerp(old_y, new_y, t)
        if option is skill:
          value = int(lerp(0x7F, 0xFF, t))
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
      title = recolor(title, GOLD)
      title = outline(title, BLACK)
      x = MARGIN + Skill.PADDING_X
      y = WINDOW_HEIGHT
      y += -MARGIN - ctx.bar.surface.get_height()
      y += -OFFSET - assets.sprites["skill"].get_height()
      y += -title.get_height() + 3
      sprites.append(Sprite(
        image=title,
        pos=(x, y),
        offset=16,
        layer="hud"
      ))

    return sprites
