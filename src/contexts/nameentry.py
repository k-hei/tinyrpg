from dataclasses import dataclass

import pygame
from pygame import Surface, SRCALPHA

import keyboard
from contexts import Context
from config import WINDOW_SIZE
from assets import load as use_assets
from palette import BLACK, WHITE, GRAY, BLUE
from filters import replace_color, darken
from cores.knight import KnightCore
from anims.walk import WalkAnim

SPACING_FACTOR = 2
TITLE_SPACING = 16
MATRIX = [
  "ABCDEF abcdef",
  "GHIJKL ghijkl",
  "MNOPQR mnopqr",
  "STUVWX stuvwx",
  "YZ,.'\" yz-:/ ",
]
MATRIX_DEADCOL = 6
FONT_NAME = "roman"
MAX_NAME_LENGTH = 7
NAME_LETTER_SPACING = 4
CHAR_MARGIN = 8
BANNER_PADDING_X = 16
BANNER_PADDING_Y = 6
BANNER_MARGIN = 8
BANNER_ITEM_ICON_SPACING = 4
BANNER_ITEM_SPACING = 12

@dataclass
class Cache:
  bg: Surface = None
  banner: Surface = None

class NameEntryContext(Context):
  matrix = MATRIX

  def __init__(ctx, default_name=""):
    ctx.name = "" # default_name
    ctx.cursor = (0, 0)
    ctx.cursor_cell = (0, 0)
    ctx.cursor_time = 0
    ctx.char = KnightCore()
    ctx.char.facing = (0, 1)
    ctx.char.anims.append(WalkAnim(period=30, vertical=True))
    ctx.cache = Cache()
    ctx.draws = 0

  def is_cell_valid(ctx, cell):
    col, row = cell
    return (row >= 0
        and col >= 0
        and row < len(ctx.matrix)
        and col < len(ctx.matrix[0]))

  def get_selected_char(ctx):
    if not ctx.is_cell_valid(ctx.cursor_cell):
      return None
    col, row = ctx.cursor_cell
    return ctx.matrix[row][col]

  def handle_move(ctx, delta):
    delta_x, delta_y = delta
    cursor_col, cursor_row = ctx.cursor_cell
    target_col = cursor_col + delta_x
    target_row = cursor_row + delta_y
    if target_col == MATRIX_DEADCOL:
      target_col += delta_x
    target_cell = (target_col, target_row)
    if ctx.is_cell_valid(target_cell):
      ctx.cursor_cell = target_cell
      ctx.cursor_time = ctx.draws
      return True
    else:
      return False

  def handle_enter(ctx):
    if len(ctx.name) == MAX_NAME_LENGTH:
      return False
    ctx.name += ctx.get_selected_char()
    if len(ctx.name) == 1:
      ctx.cache.banner = _render_banner(WINDOW_SIZE, ctx.name)
    return True

  def handle_delete(ctx):
    if len(ctx.name) == 0:
      return False
    ctx.name = ctx.name[:-1]
    if len(ctx.name) == 0:
      ctx.cache.banner = _render_banner(WINDOW_SIZE, ctx.name)
    return True

  def handle_keydown(ctx, key):
    if key in keyboard.ARROW_DELTAS:
      delta = keyboard.ARROW_DELTAS[key]
      return ctx.handle_move(delta)

    if keyboard.get_pressed(key) > 1:
      return

    if key == pygame.K_SPACE:
      return ctx.handle_enter()
    if key == pygame.K_BACKSPACE:
      return ctx.handle_delete()

  def update(ctx):
    ctx.char.update()

  def draw(ctx, surface):
    assets = use_assets()
    font = assets.ttf[FONT_NAME]
    font_size = font.get_size()

    if ctx.cache.bg is None:
      ctx.cache.bg = _render_bg(surface.get_size())
    tile_size = assets.sprites["bg_tile"].get_width()
    BG_PERIOD = 90
    t = ctx.draws % BG_PERIOD / BG_PERIOD
    x = -t * tile_size
    surface.blit(ctx.cache.bg, (x, x))

    if ctx.cache.banner is None:
      ctx.cache.banner = _render_banner(surface.get_size(), ctx.name)
    y = surface.get_height() - BANNER_MARGIN - ctx.cache.banner.get_height()
    surface.blit(ctx.cache.banner, (0, y))

    chargroup_image = _render_chargroup(ctx.char, ctx.name)
    x = surface.get_width() // 2 - chargroup_image.get_width() // 2
    y = 40
    surface.blit(chargroup_image, (x, y))

    cell_size = font_size * SPACING_FACTOR
    cols = len(ctx.matrix[0])
    rows = len(ctx.matrix)
    char_surface = Surface((
      cols * cell_size - font_size // 2,
      rows * cell_size - font_size // 2
    ), SRCALPHA)
    for row, line in enumerate(ctx.matrix):
      for col, char in enumerate(line):
        image = font.render(char, WHITE)
        x = col * cell_size
        y = row * cell_size
        char_surface.blit(image, (x, y))
    x = surface.get_width() // 2 - char_surface.get_width() // 2
    y = surface.get_height() // 2 - char_surface.get_height() // 2 + 16
    surface.blit(char_surface, (x, y))

    cursor_col, cursor_row = ctx.cursor_cell
    cursor_x, cursor_y = ctx.cursor
    cursor_x += (cursor_col * cell_size - cursor_x) / 4
    cursor_y += (cursor_row * cell_size - cursor_y) / 4
    ctx.cursor = (cursor_x, cursor_y)

    if (ctx.draws - ctx.cursor_time) % 50 < 25:
      cursor_image = assets.sprites["cursor_char0"]
    else:
      cursor_image = assets.sprites["cursor_char1"]
    x += cursor_x + font_size // 2 - cursor_image.get_width() // 2
    y += cursor_y + font_size // 2 - cursor_image.get_height() // 2
    surface.blit(cursor_image, (x, y))

    ctx.draws += 1

def _render_name(name):
  assets = use_assets()
  font = assets.ttf[FONT_NAME]
  font_size = font.get_size()
  surface = Surface((
    MAX_NAME_LENGTH * (font_size + NAME_LETTER_SPACING) - NAME_LETTER_SPACING,
    font_size
  ), SRCALPHA)
  for i in range(MAX_NAME_LENGTH):
    char = name[i] if i < len(name) else "-"
    color = GRAY if char == "-" else WHITE
    char_image = font.render(char, color)
    surface.blit(char_image, (i * (font_size + NAME_LETTER_SPACING), 0))
  return surface

def _render_chargroup(char, name):
  char_image = char.render().image
  name_image = _render_name(name)
  surface = Surface((
    char_image.get_width() + CHAR_MARGIN + name_image.get_width(),
    char_image.get_height()
  ), SRCALPHA)
  surface.blit(char_image, (0, 0))
  surface.blit(name_image, (
    char_image.get_width() + CHAR_MARGIN,
    char_image.get_height() // 2 - name_image.get_height() // 2
  ))
  return surface

def _render_bg(size):
  width, height = size
  assets = use_assets()
  tile_image = assets.sprites["bg_tile"]
  tile_width = tile_image.get_width()
  tile_height = tile_image.get_height()
  tile_surface = Surface((width + tile_width, height + tile_height))
  for row in range(tile_surface.get_height() // tile_height):
    for col in range(tile_surface.get_width() // tile_width):
      x = col * tile_width
      y = row * tile_height
      tile_surface.blit(tile_image, (x, y))
  return tile_surface

def _render_banner(size, name=None):
  width, height = size
  assets = use_assets()
  font = assets.ttf[FONT_NAME]

  banner_image = Surface((width, font.get_size() + BANNER_PADDING_Y * 2))
  banner_image.fill(BLACK)

  can_confirm = name == None or name != ""
  confirm_color = WHITE if can_confirm else GRAY
  confirm_image = font.render("Confirm", confirm_color)
  x = banner_image.get_width() - BANNER_PADDING_X - confirm_image.get_width()
  y = BANNER_PADDING_Y
  banner_image.blit(confirm_image, (x, y))

  start_image = assets.sprites["button_start"]
  start_image = replace_color(start_image, BLACK, BLUE)
  if not can_confirm:
    start_image = darken(start_image)
  x += -BANNER_ITEM_ICON_SPACING - start_image.get_width()
  y += confirm_image.get_height() / 2 -  start_image.get_height() / 2
  banner_image.blit(start_image, (x, y))

  delete_image = font.render("Delete")
  x += -BANNER_ITEM_SPACING - delete_image.get_width()
  y = BANNER_PADDING_Y
  banner_image.blit(delete_image, (x, y))

  b_image = assets.sprites["button_b"]
  b_image = replace_color(b_image, BLACK, BLUE)
  x += -BANNER_ITEM_ICON_SPACING - b_image.get_width()
  y += delete_image.get_height() / 2 -  b_image.get_height() / 2
  banner_image.blit(b_image, (x, y))

  return banner_image
