from dataclasses import dataclass
from math import cos, pi

import pygame
from pygame import Surface, Rect, SRCALPHA

import keyboard
from contexts import Context
from contexts.prompt import PromptContext, Choice
from contexts.dialogue import DialogueContext
from config import WINDOW_WIDTH, WINDOW_SIZE
from assets import load as use_assets
from palette import BLACK, WHITE, GRAY, BLUE
from filters import replace_color, darken
from comps.log import Token
from anims.walk import WalkAnim
from anims.tween import TweenAnim
from anims.flicker import FlickerAnim
from easing.expo import ease_out

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
BANNER_MARGIN = 12
BANNER_ITEM_ICON_SPACING = 4
BANNER_ITEM_SPACING = 12

class EnterAnim(TweenAnim): pass
class ExitAnim(TweenAnim): pass

class Banner:
  ENTER_DURATION = 7
  EXIT_DURATION = 4

  def __init__(banner, state_init=False):
    banner.state_target = state_init
    banner.state = banner.state_target
    banner.anim = None
    banner.active = False
    banner.surface = None

  def enter(banner, delay=0, on_end=None):
    banner.active = True
    banner.anim = EnterAnim(
      duration=banner.ENTER_DURATION,
      delay=delay,
      on_end=on_end
    )
    return True

  def exit(banner, on_end=None):
    banner.active = False
    banner.anim = ExitAnim(duration=banner.EXIT_DURATION, on_end=on_end)

  def set_state(banner, state=None):
    if state is None:
      state = banner.state_target
    banner.state = state

  def change_state(banner, state_target):
    banner.state_target = state_target
    if banner.anim is None and banner.state != banner.state_target:
      banner.exit(on_end=lambda: (
        banner.enter(on_end=lambda: (
          banner.set_state()
        ))
      ))

  def update(banner):
    if banner.anim:
      anim = banner.anim
      if anim.done:
        banner.anim = None
      anim.update()
    banner.surface = banner.render()

  def render(banner):
    assets = use_assets()
    font = assets.ttf[FONT_NAME]

    banner_width = WINDOW_WIDTH
    banner_height = font.get_size() + BANNER_PADDING_Y * 2
    banner_image = Surface((banner_width, banner_height), SRCALPHA)

    if banner.anim:
      t = banner.anim.pos
      if type(banner.anim) is ExitAnim:
        t = 1 - t
      height = banner_height * t
      banner_image.fill(0)
      pygame.draw.rect(banner_image, BLACK, Rect(
        (0, banner_height // 2 - height // 2),
        (banner_width, height)
      ))
      return banner_image

    if not banner.active:
      return banner_image

    banner_image.fill(BLACK)
    if banner.state == False:
      text_image = font.render("Please enter a name.")
      x = banner_width // 2 - text_image.get_width() // 2
      y = banner_height // 2 - text_image.get_height() // 2
      banner_image.blit(text_image, (x, y))
    elif banner.state == True:
      can_confirm = True
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

@dataclass
class Cache:
  bg: Surface = None
  surface: Surface = None

class NameEntryContext(Context):
  ENTER_DURATION = 20
  EXIT_DURATION = 10
  matrix = MATRIX

  def __init__(ctx, char, on_close=None):
    super().__init__(on_close=on_close)
    ctx.name = char.name
    ctx.cursor = (0, 0)
    ctx.cursor_cell = (0, 0)
    ctx.char = char
    ctx.char.facing = (0, 1)
    ctx.char.anims.append(WalkAnim(period=30, vertical=True))
    ctx.banner = Banner(True)
    ctx.cache = Cache()
    ctx.anims = []
    ctx.draws = 0
    ctx.exiting = False
    ctx.time_move = 0
    ctx.time_input = 0

  def enter(ctx):
    ctx.exiting = False
    ctx.anims.append(EnterAnim(duration=ctx.ENTER_DURATION, target=ctx))
    noop = lambda: None
    def on_enter():
      ctx.open(DialogueContext(script=[
        "Names may be 1-{} symbols in length.".format(MAX_NAME_LENGTH),
        "Please enter a name for this character."
      ], on_close=ctx.banner.enter))

    ctx.anims.append(EnterAnim(
      duration=25,
      delay=60,
      target="name"
    ))

    for row, line in enumerate(ctx.matrix):
      for col in range(MATRIX_DEADCOL):
        char = line[col]
        delay = (row * MATRIX_DEADCOL + col) * 2 + 15
        is_last = col == MATRIX_DEADCOL - 1 and row == len(ctx.matrix) - 1
        ctx.anims += [
          EnterAnim(
            duration=10,
            delay=delay,
            target=(col, row)
          ),
          EnterAnim(
            duration=10,
            delay=delay,
            target=(col + MATRIX_DEADCOL + 1, row),
            on_end=on_enter if is_last else noop
          )
        ]

  def exit(ctx, name=None):
    if name is None:
      name = ctx.name
    ctx.exiting = True
    ctx.anims.append(ExitAnim(
      duration=ctx.EXIT_DURATION,
      delay=60,
      target=ctx,
      on_end=lambda: ctx.close(name.strip())
    ))
    for row, line in enumerate(ctx.matrix):
      for col in range(MATRIX_DEADCOL):
        char = line[col]
        delay = row * 4
        ctx.anims += [
          ExitAnim(
            duration=10,
            delay=delay,
            target=(col, row)
          ),
          ExitAnim(
            duration=10,
            delay=delay,
            target=(col + MATRIX_DEADCOL + 1, row)
          )
        ]

  def is_cell_valid(ctx, cell):
    col, row = cell
    return (row >= 0
        and col >= 0
        and row < len(ctx.matrix)
        and col < len(ctx.matrix[0]))

  def is_name_valid(ctx, name=None):
    if name is None:
      name = ctx.name
    return name and name[0] != " "

  def get_char_at(ctx, cell=None):
    if cell is None:
      cell = ctx.cursor_cell
    col, row = cell
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
      ctx.time_move = ctx.draws
      return True
    else:
      return False

  def handle_enter(ctx):
    if len(ctx.name) == MAX_NAME_LENGTH:
      return False
    ctx.name += ctx.get_char_at()
    if len(ctx.name) == 1:
      ctx.banner.change_state(True)
    ctx.time_move = ctx.draws
    ctx.time_input = ctx.draws
    ctx.anims.append(FlickerAnim(duration=3, target="cursor"))
    return True

  def handle_delete(ctx):
    if len(ctx.name) == 0:
      return False
    ctx.name = ctx.name[:-1]
    ctx.time_input = ctx.draws
    return True

  def handle_confirm(ctx):
    if not ctx.is_name_valid():
      return False
    ctx.banner.exit()
    ctx.open(PromptContext((
      "The character's name is ",
      Token(text=ctx.name.strip().upper(), color=BLUE),
      ". Is this OK?"
    ), (
      Choice(text="Yes"),
      Choice(text="No", default=True)
    ), on_choose=lambda choice, close: (
      choice.text == "Yes" and close(chosen=True)
      or choice.text == "No" and close(chosen=False)
    ), on_close=lambda choice: (
      (choice is None or choice.text == "No")
        and ctx.banner.enter()
      or choice.text == "Yes" and ctx.exit()
    )))
    return True

  def handle_cancel(ctx):
    ctx.banner.exit()
    ctx.open(PromptContext((
      "Cancel name entry?"
    ), (
      Choice(text="Yes"),
      Choice(text="No", default=True)
    ), on_choose=lambda choice, close: (
      choice.text == "Yes" and close(chosen=True)
      or choice.text == "No" and close(chosen=False)
    ), on_close=lambda choice: (
      (choice is None or choice.text == "No")
        and ctx.banner.enter()
      or choice.text == "Yes" and ctx.exit(ctx.char.name)
    )))
    return True

  def handle_keydown(ctx, key):
    if ctx.anims:
      return

    if ctx.child:
      return ctx.child.handle_keydown(key)

    key_time = keyboard.get_pressed(key)
    if (key in keyboard.ARROW_DELTAS
    and (key_time == 1 or key_time > 30 and key_time % 2)):
      delta = keyboard.ARROW_DELTAS[key]
      return ctx.handle_move(delta)

    if key_time > 1:
      return

    if key == pygame.K_SPACE:
      return ctx.handle_enter()
    if key == pygame.K_BACKSPACE:
      return ctx.handle_delete()
    if key == pygame.K_RETURN:
      return ctx.handle_confirm()
    if key == pygame.K_ESCAPE:
      return ctx.handle_cancel()

  def draw(ctx, surface):
    if not ctx.anims and ctx.exiting:
      return

    assets = use_assets()
    font = assets.ttf[FONT_NAME]
    font_size = font.get_size()

    if ctx.cache.surface is None:
      ctx.cache.surface = Surface(surface.get_size())

    if ctx.cache.bg is None:
      ctx.cache.bg = _render_bg(surface.get_size())
    tile_size = assets.sprites["bg_tile"].get_width()
    BG_PERIOD = 90
    t = ctx.draws % BG_PERIOD / BG_PERIOD
    x = -t * tile_size
    ctx.cache.surface.blit(ctx.cache.bg, (x, x))

    ctx.banner.update()
    banner_image = ctx.banner.surface
    y = surface.get_height() - BANNER_MARGIN - banner_image.get_height()
    ctx.cache.surface.blit(banner_image, (0, y))

    ctx.char.update()
    chargroup_time = ctx.draws - ctx.time_input
    cursor_anim = next((a for a in ctx.anims if a.target == "cursor"), None)
    if ctx.child or ctx.anims and not cursor_anim:
      chargroup_time = -1
    chargroup_name = ctx.name
    name_anim = next((a for a in ctx.anims if a.target == "name"), None)
    if name_anim:
      t = name_anim.pos
      index = int(t * len(ctx.name))
      chargroup_name = ctx.name[:index]
    chargroup_image = _render_chargroup(ctx.char, chargroup_name, chargroup_time)
    x = surface.get_width() // 2 - chargroup_image.get_width() // 2
    y = 40
    ctx.cache.surface.blit(chargroup_image, (x, y))

    cell_size = font_size * SPACING_FACTOR
    cols = len(ctx.matrix[0])
    rows = len(ctx.matrix)
    char_surface = Surface((
      cols * cell_size - font_size // 2,
      rows * cell_size - font_size // 2 + 8
    ), SRCALPHA)
    for row, line in enumerate(ctx.matrix):
      for col, char in enumerate(line):
        x = col * cell_size
        y = row * cell_size
        char_color = WHITE
        char_anim = next((a for a in ctx.anims if a.target == (col, row)), None)
        if char_anim:
          if char_anim.pos or type(char_anim) is ExitAnim:
            t = char_anim.pos
            if type(char_anim) is EnterAnim:
              t = ease_out(t)
            elif type(char_anim) is ExitAnim:
              t = 1 - t
            y = y - 8 + t * 8
            if char_anim.pos:
              char_color = GRAY
          else:
            char_color = None
        elif ctx.exiting:
          char_color = None
        if char_color:
          char_image = font.render(char, char_color)
          char_surface.blit(char_image, (x, y + 8))
    x = surface.get_width() // 2 - char_surface.get_width() // 2
    y = surface.get_height() // 2 - char_surface.get_height() // 2 + 8
    ctx.cache.surface.blit(char_surface, (x, y))

    cursor_col, cursor_row = ctx.cursor_cell
    cursor_x, cursor_y = ctx.cursor
    cursor_x += (cursor_col * cell_size - cursor_x) / 4
    cursor_y += (cursor_row * cell_size - cursor_y) / 4
    ctx.cursor = (cursor_x, cursor_y)

    cursor_anim = next((a for a in ctx.anims if a.target == "cursor"), None)
    if not ctx.child and (not ctx.anims or cursor_anim):
      time_move = ctx.draws - ctx.time_move
      if time_move % 50 < 25:
        cursor_image = assets.sprites["cursor_char0"]
      else:
        cursor_image = assets.sprites["cursor_char1"]
      if cursor_anim and not cursor_anim.visible:
        cursor_image = None
      if cursor_image:
        x += cursor_x + font_size // 2 - cursor_image.get_width() // 2
        y += cursor_y + font_size // 2 - cursor_image.get_height() // 2 + 8
        ctx.cache.surface.blit(cursor_image, (x, y))

    surface_clip = ctx.cache.surface
    surface_rect = surface.get_rect()
    for anim in ctx.anims:
      if anim.done:
        ctx.anims.remove(anim)
      anim.update()
      if anim.target is ctx:
        t = anim.pos
        if type(anim) is EnterAnim:
          t = ease_out(t)
        elif type(anim) is ExitAnim:
          t = 1 - t
        height = surface.get_height() * t
        y = surface.get_height() // 2 - height // 2
        surface_rect = Rect((0, y), (surface.get_width(), height))

    surface.blit(ctx.cache.surface, (0, surface_rect.top), area=surface_rect)
    if ctx.child:
      ctx.child.draw(surface)

    ctx.draws += 1

def _render_name(name, draws):
  assets = use_assets()
  font = assets.ttf[FONT_NAME]
  font_size = font.get_size()
  surface = Surface((
    MAX_NAME_LENGTH * (font_size + NAME_LETTER_SPACING) - NAME_LETTER_SPACING,
    font_size
  ), SRCALPHA)
  for i in range(MAX_NAME_LENGTH):
    if i == len(name) and draws != -1:
      char = "_"
      t = draws % 60 / 60
      a = (cos(2 * pi * t) + 1) / 2 + 1 / 4
      if a >= 2 / 3:
        color = WHITE
      elif a >= 1 / 3:
        color = GRAY
      else:
        char = " "
    elif i < len(name):
      char = name[i]
      color = WHITE
    else:
      char = "-"
      color = GRAY
    if char == " ":
      continue
    char_image = font.render(char, color)
    surface.blit(char_image, (i * (font_size + NAME_LETTER_SPACING), 0))
  return surface

def _render_chargroup(char, name, draws):
  char_image = char.render().image
  name_image = _render_name(name, draws)
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
