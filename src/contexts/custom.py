from assets import load as use_assets
from contexts import Context
from comps.bar import Bar
from comps.skill import Skill
from skills import get_skill_text
from filters import replace_color, recolor, outline
from text import render as render_text
import pygame
from pygame import Rect
import palette
import keyboard
from comps.piece import Piece

from actors.knight import Knight
from actors.mage import Mage

SPACING_X = 4
SPACING_Y = 4
SKILL_MARGIN_Y = 1
SKILL_NUDGE_LEFT = 8
SKILLS_VISIBLE = 4
TAB_OVERLAP = 3
DECK_PADDING_X = 8
DECK_PADDING_Y = 10

class CustomContext(Context):
  def __init__(ctx, parent, on_close=None):
    super().__init__(parent)
    ctx.on_close = on_close
    ctx.char = parent.hero
    ctx.index = 0
    ctx.offset = 0
    ctx.arrange = False
    ctx.cursor = (0, 0)
    ctx.pieces = parent.skill_builds[ctx.char]
    ctx.matrix_size = (4, 4)
    ctx.bar = Bar()
    ctx.bar.enter()
    ctx.update_bar()

  def update_bar(ctx):
    skill = ctx.get_selected_skill()
    skill_text = get_skill_text(skill)
    ctx.bar.print(skill_text)

  def get_char_skills(ctx):
    return [s for s in ctx.parent.skill_pool if type(ctx.char) in s.users]

  def get_selected_skill(ctx):
    return ctx.get_char_skills()[ctx.index]

  def is_skill_used(ctx, skill):
    return skill in [skill for skill, cell in ctx.pieces]

  def is_cell_in_bounds(ctx, target):
    matrix_width, matrix_height = ctx.matrix_size
    x, y = target
    return x >= 0 and y >= 0 and x < matrix_width and y < matrix_height

  def is_cell_empty(ctx, target):
    for skill, cell in ctx.pieces:
      for block in Piece.offset(skill.blocks, cell):
        if block == target:
          return False
    return True

  def is_cell_valid(ctx, cell):
    return ctx.is_cell_in_bounds(cell) and ctx.is_cell_empty(cell)

  def handle_move_piece(ctx, delta):
    delta_x, delta_y = delta
    cursor_x, cursor_y = ctx.cursor
    new_cursor = (cursor_x + delta_x, cursor_y + delta_y)
    skill = ctx.get_selected_skill()
    for block in Piece.offset(skill.blocks, new_cursor):
      if not ctx.is_cell_in_bounds(block):
        break
    else:
      ctx.cursor = new_cursor

  def handle_place_piece(ctx):
    skill = ctx.get_selected_skill()
    for block in Piece.offset(skill.blocks, ctx.cursor):
      if not ctx.is_cell_empty(block):
        break
    else:
      ctx.pieces.append((skill, ctx.cursor))
      ctx.stop_arrange()

  def stop_arrange(ctx):
    ctx.arrange = False
    ctx.cursor = (0, 0)

  def handle_swap_char(ctx):
    game = ctx.parent
    if ctx.char is game.hero:
      ctx.char = game.ally
    elif ctx.char is game.ally:
      ctx.char = game.hero
    ctx.pieces = game.skill_builds[ctx.char]
    ctx.index = 0
    ctx.offset = 0
    ctx.update_bar()

  def handle_move_index(ctx, delta):
    max_index = len(ctx.get_char_skills()) - 1
    old_index = ctx.index
    ctx.index += delta
    if ctx.index < 0:
      ctx.index = 0
    if ctx.index > max_index:
      ctx.index = max_index
    if ctx.index != old_index:
      ctx.update_bar()
    ctx.offset = max(0, ctx.index - (SKILLS_VISIBLE - 1))

  def handle_select_piece(ctx):
    skill = ctx.get_selected_skill()
    if not ctx.is_skill_used(skill):
      ctx.arrange = True
    else:
      index = [skill for skill, cell in ctx.pieces].index(skill)
      ctx.pieces.pop(index)

  def handle_keydown(ctx, key):
    if keyboard.get_pressed(key) != 1:
      return

    if ctx.arrange:
      if key in keyboard.ARROW_DELTAS:
        ctx.handle_move_piece(delta=keyboard.ARROW_DELTAS[key])

      if key == pygame.K_RETURN or key == pygame.K_SPACE:
        ctx.handle_place_piece()

      if key == pygame.K_ESCAPE or key == pygame.K_BACKSPACE:
        ctx.stop_arrange()
    else:
      if key == pygame.K_TAB:
        ctx.handle_swap_char()

      if key == pygame.K_UP or key == pygame.K_w:
        ctx.handle_move_index(-1)

      if key == pygame.K_DOWN or key == pygame.K_s:
        ctx.handle_move_index(1)

      if key == pygame.K_RETURN or key == pygame.K_SPACE:
        ctx.handle_select_piece()

      if key == pygame.K_ESCAPE:
        ctx.close()

  def render(ctx):
    assets = use_assets()
    circle_knight = assets.sprites["circle_knight"]
    circle_mage = assets.sprites["circle_mage"]
    if type(ctx.char) is Knight:
      circle_mage = replace_color(circle_mage, palette.WHITE, palette.GRAY)
      circle_mage = replace_color(circle_mage, palette.BLUE, palette.BLUE_DARK)
    elif type(ctx.char) is Mage:
      circle_knight = replace_color(circle_knight, palette.WHITE, palette.GRAY)
      circle_knight = replace_color(circle_knight, palette.BLUE, palette.BLUE_DARK)
    deck = assets.sprites["deck"]
    tab = assets.sprites["deck_tab"]
    tab_inactive = replace_color(tab, palette.WHITE, palette.GRAY)
    skills = ctx.get_char_skills()
    skill = Skill.render(skills[0])

    tab_y = circle_knight.get_height() + SPACING_Y
    deck_y = tab_y + tab.get_height() - TAB_OVERLAP
    surface = pygame.Surface((
      deck.get_width() + SPACING_X + skill.get_width() + SKILL_NUDGE_LEFT,
      deck_y + deck.get_height() + 1
    ))
    surface.set_colorkey(0xFF00FF)
    surface.fill(0xFF00FF)
    surface.blit(circle_knight, (0, 0))
    surface.blit(circle_mage, (circle_knight.get_width() + SPACING_X, 0))

    # surface.blit(tab_inactive, (tab.get_width() - 1, tab_y))
    # surface.blit(tab_inactive, (tab.get_width() * 2 - 2, tab_y))
    surface.blit(deck, (0, deck_y))
    surface.blit(tab, (0, tab_y))

    text = render_text("1", assets.fonts["smallcaps"])
    surface.blit(text, (8, tab_y + 8))

    grid_x = DECK_PADDING_X
    grid_y = deck_y + DECK_PADDING_Y
    for skill, (col, row) in ctx.pieces:
      sprite = Piece.render(skill.blocks, Skill.get_color(skill), Skill.get_icon(skill))
      surface.blit(sprite, (
        grid_x + col * Piece.BLOCK_SIZE,
        grid_y + row * Piece.BLOCK_SIZE,
      ))

    cursor_x, cursor_y = ctx.cursor
    skill = ctx.get_selected_skill()
    if ctx.arrange:
      blocks = skill.blocks
      sprite = Piece.render(blocks, Skill.get_color(skill), Skill.get_icon(skill))
      surface.blit(sprite, (
        grid_x + cursor_x * Piece.BLOCK_SIZE,
        grid_y + cursor_y * Piece.BLOCK_SIZE - 4,
      ))

    texts = []
    y = deck_y
    visible_start = ctx.offset
    visible_end = SKILLS_VISIBLE + ctx.offset
    visible_skills = skills[visible_start:visible_end]
    for i, skill in enumerate(visible_skills):
      index = i + ctx.offset
      if ctx.arrange and index != ctx.index:
        sprite = Skill.render(skill, False)
      else:
        sprite = Skill.render(skill)
      x = deck.get_width() + SPACING_X
      if index == ctx.index:
        subspr = sprite.subsurface(Rect(
          Skill.PADDING_X,
          Skill.PADDING_Y,
          sprite.get_width() - Skill.PADDING_X * 2,
          sprite.get_height() - Skill.PADDING_Y * 2
        ))
        sprite = replace_color(sprite, palette.WHITE, palette.YELLOW)
        sprite.blit(subspr, (Skill.PADDING_X, Skill.PADDING_Y))
        x += SKILL_NUDGE_LEFT
      if ctx.is_skill_used(skill):
        color = Skill.get_color(skill)
        subspr = sprite.subsurface(Rect(3, 3, sprite.get_width() - 6, sprite.get_height() - 6))
        subspr = replace_color(subspr, color, palette.darken(color))
        subspr = replace_color(subspr, palette.WHITE, palette.GRAY)
        sprite.blit(subspr, (3, 3))
        surface.blit(sprite, (x, y))
        text = render_text("ON", assets.fonts["smallcaps"])
        text = recolor(text, palette.YELLOW)
        text = outline(text, (0, 0, 0))
        texts.append((text, x + sprite.get_width() - text.get_width() - 6, y + sprite.get_height() - 6))
      surface.blit(sprite, (x, y))
      y += sprite.get_height() + SKILL_MARGIN_Y

    for text, x, y in texts:
      surface.blit(text, (x, y))

    return surface

  def draw(ctx, surface):
    assets = use_assets()
    sprite = ctx.render()
    surface.blit(sprite, (
      surface.get_width() // 2 - sprite.get_width() // 2 + SKILL_NUDGE_LEFT,
      (surface.get_height() - assets.sprites["statusbar"].get_height() - Bar.MARGIN * 2) // 2 - sprite.get_height() // 2
    ))
    ctx.bar.draw(surface)
