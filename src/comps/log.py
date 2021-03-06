from pygame import Surface, Rect, SRCALPHA
from assets import load as use_assets
from text import render as render_text, find_width as find_text_width
from lib.filters import recolor, outline, shadow
from anims.tween import TweenAnim
from easing.expo import ease_out, ease_in
from config import WINDOW_WIDTH, WINDOW_HEIGHT
from lib.sprite import Sprite
from colors.palette import BLACK

class EnterAnim(TweenAnim): pass
class ExitAnim(TweenAnim): pass

class Log:
  ROW_COUNT = 3
  SCROLL_SPEED = 1
  PADDING_X = 12
  PADDING_Y = 15
  MARGIN_LEFT = 12
  MARGIN_BOTTOM = 8
  ENTER_DURATION = 15
  EXIT_DURATION = 5
  HANG_DURATION = 180
  FONT_NAME = "normal"
  LINE_SPACING = 4

  def __init__(log, autohide=True, align="center", side="bottom", silent=False):
    log.autohide = autohide
    log.align = align
    log.side = side
    log.silent = silent
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
    log.on_end = None

  def print(log, tokens, on_end=None):
    message = Message(tokens)
    if not log.silent:
      print(str(message))
    if not log.active and (log.anim is None or log.anim.done):
      log.enter()
    if log.clean and log.messages:
      log.index += 1
      log.row += 1
      log.col = 0
      log.cursor_x = 0
    log.messages.append(message)
    log.clean = 0
    log.on_end = on_end

  def enter(log):
    log.active = True
    log.anim = EnterAnim(duration=Log.ENTER_DURATION)

  def exit(log, on_end=None):
    if log.active:
      log.active = False
      log.anim = ExitAnim(
        duration=Log.EXIT_DURATION,
        on_end=lambda: (
          log.reset(),
          on_end and on_end()
        )
      )
    elif on_end:
      on_end()

  def clear(log):
    log.messages = []
    log.lines = []
    log.index = 0
    log.row = 0
    log.col = 0
    log.cursor_x = 0
    log.cursor_y = 0
    log.surface = None

  def reset(log):
    log.clear()
    log.box = None

  def skip(log):
    if log.anim:
      return
    while not log.clean:
      log.render()

  def render(log):
    assets = use_assets()
    bg = assets.sprites["log_parchment"]
    font = assets.ttf[Log.FONT_NAME]
    _, char_height = font.size()
    line_height = char_height + Log.LINE_SPACING

    if not log.clean and log.active and log.anim is None:
      target_height = (log.row + 1) * line_height
      if log.surface is None or target_height > log.surface.get_height():
        log.surface = Surface((
          log.box.get_width() - Log.PADDING_X * 2,
          target_height
        ), SRCALPHA)
      if log.row + 1 > len(log.lines):
        COLOR_KEY = (255, 0, 255)
        line = Surface((log.surface.get_width(), line_height))
        line.fill(COLOR_KEY)
        line.set_colorkey(COLOR_KEY)
        log.lines.append(line)
      message = log.messages[log.index]
      char = message[log.col]
      if char == "\n":
        log.col += 1
        log.row += 1
        log.cursor_x = 0
        return log.render()
      token = message.get_token_at(log.col)
      if log.col == 0 or char in (" ", "\n"):
        next_space = message.find(" ", log.col + 1)
        if next_space == -1:
          next_space = message.find("\n", log.col + 1)
        if next_space == -1:
          word = message[log.col+1:]
        else:
          word = message[log.col+1:next_space]
        word_width, _ = font.size(word)
        space_width, _ = font.size(" ")
        if log.cursor_x + space_width + word_width > log.surface.get_width():
          log.col += 1
          log.row += 1
          log.cursor_x = 0
          return log.render()
      char_sprite = font.render(char, token.color or BLACK)
      log.lines[-1].blit(char_sprite, (log.cursor_x, 0))
      for row, line in enumerate(log.lines):
        log.surface.blit(line, (0, row * line_height))
      log.cursor_x += char_sprite.get_width() # - 1
      if log.col < len(message) - 1:
        log.col += 1
      elif log.index < len(log.messages) - 1:
        log.index += 1
        log.col = 0
        log.row += 1
        log.cursor_x = 0
      else:
        log.clean = 1
        if log.on_end:
          log.on_end()

    target_row = log.row
    if target_row >= Log.ROW_COUNT - 1 and target_row == len(log.lines) - 1:
      target_row -= (Log.ROW_COUNT - 1)
    target_y = target_row * line_height
    log.cursor_y += min(Log.SCROLL_SPEED, target_y - log.cursor_y)

    if log.surface and (log.clean <= 1 or log.cursor_y != target_y):
      rect_y = log.cursor_y
      rect_height = line_height * min(Log.ROW_COUNT, len(log.lines))
      if rect_y + rect_height > log.surface.get_height():
        rect_y = log.surface.get_height() - rect_height
      rect = Rect(
        (0, rect_y),
        (log.box.get_width() - Log.PADDING_X * 2, rect_height)
      )
      log.box = bg.copy()
      log.box.blit(log.surface.subsurface(rect), (Log.PADDING_X, Log.PADDING_Y))

    if log.clean:
      log.clean += 1
    if log.clean == Log.HANG_DURATION and log.autohide:
      log.exit()

    if not log.box:
      log.box = bg.copy()
    return log.box

  def update(log):
    sprite = log.render()
    if sprite is None:
      return
    y = sprite.get_height() + Log.MARGIN_BOTTOM
    if log.anim:
      anim = log.anim
      if anim.done:
        log.anim = None
      t = anim.update()
      if type(anim) == EnterAnim:
        log.y = y * ease_out(t)
      elif type(anim) == ExitAnim:
        log.y = y * (1 - t)
    elif log.active:
      log.y = y
    else:
      log.y = 0

  def view(log):
    sprites = []
    log.update()
    if log.box is None:
      return []
    if log.align == "left":
      log.x = Log.MARGIN_LEFT
    elif log.align == "center":
      log.x = WINDOW_WIDTH // 2 - log.box.get_width() // 2
    x = log.x
    y = log.y
    if log.side == "top":
      y = log.y - log.box.get_height()
    elif log.side == "bottom":
      y = WINDOW_HEIGHT - log.y
    sprites = [Sprite(
      image=log.box,
      pos=(x, y),
      layer="log"
    )]
    return sprites

def expand_tokens(tokens):
  if type(tokens) is str:
    return [Token(text=tokens)]
  result = []
  for token in tokens:
    if type(token) is tuple:
      result.extend(expand_tokens(token))
    elif type(token) is str and token:
      result.append(Token(token))
    elif type(token) is Token:
      result.append(token)
  return result

class Message:
  def __init__(message, data):
    message.tokens = expand_tokens(data)

  def __len__(message):
    length = 0
    for token in message.tokens:
      length += len(token)
    return length

  def __str__(message):
    string = ""
    for token in message.tokens:
      string += str(token)
    return string

  def __getitem__(message, key):
    if type(key) is slice:
      return str(message)[key.start:key.stop]
    else:
      return message.get_char_at(key)

  def get_char_at(message, index):
    for i, token in enumerate(message.tokens):
      if index < len(token):
        return token[index]
      index -= len(token)
    return None

  def get_token_at(message, index):
    for i, token in enumerate(message.tokens):
      if index < len(token):
        return token
      index -= len(token)
    return None

  def get_at(message, index):
    for i, token in enumerate(message.tokens):
      if index < len(token):
        return (i, index)
      index -= len(token)
    return (-1, -1)

  def find(message, sub, start=0, end=None):
    if end is None:
      end = len(message)
    return str(message).find(sub, start, end)

class Token:
  def __init__(token, text="", color=None, bold=False):
    token.text = text
    token.color = color
    token.bold = bold

  def __len__(token):
    return len(token.text)

  def __str__(token):
    return token.text

  def __getitem__(token, key):
    return token.text[key]
