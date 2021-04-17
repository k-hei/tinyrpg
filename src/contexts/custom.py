from assets import load as use_assets
from contexts import Context
from comps.skill import Skill
from filters import replace_color, recolor
import pygame
from pygame import Rect
import palette
import keyboard
from comps.piece import Piece

from actors.knight import Knight
from actors.mage import Mage

SPACING_X = 4
SPACING_Y = 4
SKILL_MARGIN_Y = 0
SKILL_NUDGE_LEFT = 8
TAB_OVERLAP = 3
DECK_PADDING = 8

class CustomContext(Context):
  def __init__(ctx, parent, on_close=None):
    super().__init__(parent)
    ctx.on_close = on_close
    ctx.char = parent.hero
    ctx.index = 0
    ctx.arrange = False
    ctx.cursor = (0, 0)
    ctx.pieces = []
    ctx.matrix_size = (4, 6)

  def get_selected_skill(ctx):
    return ctx.parent.skills[ctx.char][ctx.index]

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

  def handle_keydown(ctx, key):
    if keyboard.get_pressed(key) != 1:
      return

    if ctx.arrange:
      if key in keyboard.ARROW_DELTAS:
        delta_x, delta_y = keyboard.ARROW_DELTAS[key]
        cursor_x, cursor_y = ctx.cursor
        new_cursor = (cursor_x + delta_x, cursor_y + delta_y)
        skill = ctx.get_selected_skill()
        for block in Piece.offset(skill.blocks, new_cursor):
          if not ctx.is_cell_in_bounds(block):
            break
        else:
          ctx.cursor = new_cursor

      if key == pygame.K_RETURN or key == pygame.K_SPACE:
        skill = ctx.get_selected_skill()
        for block in Piece.offset(skill.blocks, ctx.cursor):
          if not ctx.is_cell_empty(block):
            break
        else:
          ctx.pieces.append((skill, ctx.cursor))
          ctx.arrange = False
          ctx.cursor = (0, 0)

      if key == pygame.K_ESCAPE or key == pygame.K_BACKSPACE:
        ctx.arrange = False
        ctx.cursor = (0, 0)
    else:
      if key == pygame.K_TAB:
        if ctx.char is ctx.parent.hero:
          ctx.char = ctx.parent.ally
        elif ctx.char is ctx.parent.ally:
          ctx.char = ctx.parent.hero
        ctx.index = 0

      if key == pygame.K_UP or key == pygame.K_w:
        ctx.index = max(0, ctx.index - 1)

      if key == pygame.K_DOWN or key == pygame.K_s:
        ctx.index = min(len(ctx.parent.skills[ctx.char]) - 1, ctx.index + 1)

      if key == pygame.K_RETURN or key == pygame.K_SPACE:
        skill = ctx.get_selected_skill()
        if not ctx.is_skill_used(skill):
          ctx.arrange = True
        else:
          index = [skill for skill, cell in ctx.pieces].index(skill)
          ctx.pieces.pop(index)

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
    skill = Skill.render(ctx.char.skill)

    tab_y = circle_knight.get_height() + SPACING_Y
    deck_y = tab_y + tab.get_height() - TAB_OVERLAP
    surface = pygame.Surface((
      deck.get_width() + SPACING_X + skill.get_width() + SKILL_NUDGE_LEFT,
      deck_y + deck.get_height()
    ))
    surface.set_colorkey(0xFF00FF)
    surface.fill(0xFF00FF)
    surface.blit(circle_knight, (0, 0))
    surface.blit(circle_mage, (circle_knight.get_width() + SPACING_X, 0))

    surface.blit(tab_inactive, (tab.get_width() - 1, tab_y))
    surface.blit(tab_inactive, (tab.get_width() * 2 - 2, tab_y))
    surface.blit(deck, (0, deck_y))
    surface.blit(tab, (0, tab_y))

    grid_x = DECK_PADDING
    grid_y = deck_y + DECK_PADDING
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

    y = deck_y
    for i, skill in enumerate(ctx.parent.skills[ctx.char]):
      if ctx.arrange and i != ctx.index:
        sprite = Skill.render(skill, False)
      else:
        sprite = Skill.render(skill)
      x = deck.get_width() + SPACING_X
      if i == ctx.index:
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
        sprite = replace_color(sprite, palette.WHITE, palette.GRAY)
      surface.blit(sprite, (x, y))
      y += sprite.get_height() + SKILL_MARGIN_Y
    return surface

  def draw(ctx, surface):
    sprite = ctx.render()
    surface.blit(sprite, (
      surface.get_width() // 2 - sprite.get_width() // 2 + SKILL_NUDGE_LEFT,
      surface.get_height() // 2 - sprite.get_height() // 2
    ))
