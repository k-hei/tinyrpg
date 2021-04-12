from pygame import Surface
from text import render as render_text
from anims.tween import TweenAnim
from easeexpo import ease_out, ease_in

COLOR_KEY = (0xFF, 0x00, 0xFF)

class EnterAnim(TweenAnim): pass
class ExitAnim(TweenAnim): pass

class Log:
  ROW_COUNT = 2
  BOX_WIDTH = 240
  BOX_HEIGHT = 48
  INSET_X = 11
  INSET_Y = 13
  ENTER_DURATION = 15
  EXIT_DURATION = 7
  HANG_DURATION = 180

  def __init__(log):
    log.messages = []
    log.cache = []
    log.y = 0
    log.row = -1
    log.col = 0
    log.offset = 0
    log.dirty = False
    log.active = False
    log.clean_frames = Log.HANG_DURATION
    log.box = Surface((Log.BOX_WIDTH, Log.BOX_HEIGHT))
    log.surface = None
    log.anim = None

  def print(log, message):
    log.messages.append(message)
    if not log.active and log.anim is None:
      log.active = True
      log.dirty = False
      log.anim = EnterAnim(duration=Log.ENTER_DURATION)
    if not log.dirty:
      log.row += 1
      log.col = 0
      log.dirty = True
      log.clean_frames = 0

  def exit(log):
    log.anim = ExitAnim(
      duration=Log.EXIT_DURATION,
      on_end=lambda: log.reset()
    )

  def reset(log):
    log.messages = []
    log.cache = []
    log.row = -1
    log.offset = 0
    log.active = False

  def render(log, bg, font):
    line_height = font.char_height + font.line_spacing
    log.box.blit(bg, (0, 0))
    log.surface = Surface((Log.BOX_WIDTH - Log.INSET_X * 2, line_height * Log.ROW_COUNT))
    log.surface.fill(COLOR_KEY)
    log.surface.set_colorkey(COLOR_KEY)
    is_cache_dirty = log.row >= len(log.cache) or log.row >= 0 and log.cache[log.row]["dirty"]
    if log.anim is None and log.dirty and log.row < len(log.messages) and is_cache_dirty:
      if log.row >= len(log.cache):
        surface = Surface((log.surface.get_width(), line_height))
        surface.fill(COLOR_KEY)
        surface.set_colorkey(COLOR_KEY)
        log.cache.append({
          "x": 0,
          "dirty": True,
          "surface": surface
        })
      line = log.cache[log.row]
      message = log.messages[log.row]
      char = message[log.col]
      text = render_text(char, font)
      line["surface"].blit(text, (line["x"], 0))
      line["x"] += text.get_width()
      if log.col < len(message) - 1:
        log.col += 1
      elif log.row < len(log.messages) - 1:
        log.row += 1
        log.col = 0
        line["dirty"] = False
      else:
        log.dirty = False

    if not log.dirty:
      log.clean_frames += 1
      if log.clean_frames == Log.HANG_DURATION:
        log.exit()

    if log.row >= Log.ROW_COUNT:
      log.offset += (log.row - 1 - log.offset) / 8

    for i in range(len(log.cache)):
      line = log.cache[i]
      y = round((i - log.offset) * line_height)
      log.surface.blit(line["surface"], (0, y))

    y = -log.box.get_height() - 8
    if log.anim:
      anim = log.anim
      t = anim.update()
      if type(anim) == EnterAnim:
        log.y = y * ease_out(t)
      elif type(anim) == ExitAnim:
        log.y = y * ease_in(1 - t)
      if anim.done:
        log.anim = None
    elif log.active:
      log.y = y
    else:
      log.y = 0

    log.box.blit(log.surface, (Log.INSET_X, Log.INSET_Y))
    return log.box
