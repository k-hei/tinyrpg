from pygame import Surface, Rect
from assets import load as use_assets
from text import render as render_text, find_width as find_text_width
from filters import recolor, outline
from anims.tween import TweenAnim
from easing.expo import ease_out, ease_in

COLOR_KEY = (0xFF, 0x00, 0xFF)

class EnterAnim(TweenAnim): pass
class ExitAnim(TweenAnim): pass

class Log:
  ROW_COUNT = 2
  PADDING_X = 12
  PADDING_Y = 22
  MARGIN_LEFT = 12
  MARGIN_BOTTOM = 8
  ENTER_DURATION = 15
  EXIT_DURATION = 7
  HANG_DURATION = 180

  def __init__(log):
    log.messages = []
    log.lines = []
    log.index = 0
    log.row = 0
    log.col = 0
    log.cursor_x = 0
    log.cursor_y = 0
    log.active = False
    log.clean = 1
    log.box = None
    log.surface = None
    log.anim = None

  def print(log, message):
    print(message)
    if not log.active and log.anim is None:
      log.enter()
    if log.clean and log.messages:
      log.index += 1
      log.row += 1
      log.col = 0
      log.cursor_x = 0
    log.messages.append(message)
    log.clean = 0

  def enter(log):
    if not log.active:
      log.active = True
      log.anim = EnterAnim(duration=Log.ENTER_DURATION)

  def exit(log):
    if log.active:
      log.active = False
      log.anim = ExitAnim(
        duration=Log.EXIT_DURATION,
        on_end=log.reset
      )

  def clear(log):
    log.messages = []
    log.lines = []
    log.index = 0
    log.row = 0
    log.col = 0
    log.cursor_x = 0
    log.cursor_y = 0

  def reset(log):
    log.clear()

  def render(log):
    assets = use_assets()
    bg = assets.sprites["log_parchment"]
    font = assets.fonts["standard"]
    line_height = font.char_height + font.line_spacing

    log.box = bg.copy()
    target_height = (log.row + 1) * line_height

    if log.surface is None or target_height > log.surface.get_height():
      log.surface = Surface((
        log.box.get_width() - Log.PADDING_X * 2,
        target_height
      ))
      log.surface.set_colorkey(COLOR_KEY)
      log.surface.fill(COLOR_KEY)

    if not log.clean and log.row + 1 > len(log.lines):
      line = Surface((log.surface.get_width(), line_height)).convert_alpha()
      line.set_colorkey(COLOR_KEY)
      line.fill(COLOR_KEY)
      log.lines.append(line)
      print("new line!")

    if not log.clean and log.anim is None:
      message = log.messages[log.index]
      char = message[log.col]
      if log.col == 0 or char == " ":
        next_space = message.find(" ", log.col + 1)
        if next_space == -1:
          word = message[log.col+1:]
        else:
          word = message[log.col+1:next_space]
        if log.cursor_x + find_text_width(word, font) > log.surface.get_width():
          log.col += 1
          log.row += 1
          log.cursor_x = 0
          return log.render()
      char_sprite = render_text(char, font)
      char_sprite = recolor(char_sprite, (0, 0, 0))
      print(log.cursor_x, len(log.lines) - 1, char)
      log.lines[-1].blit(char_sprite, (log.cursor_x, 0))
      for row, line in enumerate(log.lines):
        log.surface.blit(line, (0, row * line_height))
      log.cursor_x += char_sprite.get_width()
      if log.col < len(message) - 1:
        log.col += 1
      elif log.index < len(log.messages) - 1:
        log.index += 1
        log.col = 0
        log.row += 1
        log.cursor_x = 0
      else:
        log.clean = 1

    target_row = log.row
    if target_row >= Log.ROW_COUNT - 1 and target_row == len(log.lines) - 1:
      target_row -= 1
    target_y = target_row * line_height
    log.cursor_y += (target_y - log.cursor_y) / 8

    if log.clean:
      log.clean += 1
      if log.clean == Log.HANG_DURATION:
        log.exit()

    y = -log.box.get_height() - Log.MARGIN_BOTTOM
    if log.anim:
      anim = log.anim
      t = anim.update()
      if type(anim) == EnterAnim:
        log.y = y * ease_out(t)
      elif type(anim) == ExitAnim:
        log.y = y * ease_in(1 - t)
      if anim.done:
        log.anim = None
      if anim.done and not log.active:
        log.surface = None
    elif log.active:
      log.y = y
    else:
      log.y = 0

    if log.surface:
      rect_y = log.cursor_y
      rect_height = line_height * min(Log.ROW_COUNT, len(log.lines))
      if rect_y + rect_height > log.surface.get_height():
        rect_y = log.surface.get_height() - rect_height
      rect = Rect(
        (0, rect_y),
        (log.box.get_width() - Log.PADDING_X * 2, rect_height)
      )
      print(rect, log.surface.get_height())
      log.box.blit(log.surface.subsurface(rect), (Log.PADDING_X, Log.PADDING_Y))
    return log.box

  def draw(log, surface):
    surface.blit(log.render(), (
      Log.MARGIN_LEFT,
      surface.get_height() + log.y
    ))
