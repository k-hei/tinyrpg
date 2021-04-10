from pygame import Surface
from text import render as render_text
from anim import Anim
from easeexpo import ease_out, ease_in

COLOR_KEY = (0xFF, 0x00, 0XFF)

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
    log.y = 0
    log.row = -1
    log.col = 0
    log.offset = 0
    log.dirty = False
    log.clean_frames = 0
    log.box = Surface((Log.BOX_WIDTH, Log.BOX_HEIGHT))
    log.surface = None
    log.cache = []
    log.anim = None

  def print(log, message):
    log.messages.append(message)
    if log.row == -1 or log.clean_frames > log.HANG_DURATION and log.anim is None:
      log.anim = Anim(Log.ENTER_DURATION, {
        "kind": "enter",
        "target": log
      })
    if not log.dirty:
      log.row += 1
      log.col = 0
      log.dirty = True
      log.clean_frames = False

  def render(log, bg, font):
    line_height = font.char_height + font.line_spacing
    log.box.blit(bg, (0, 0))
    log.surface = Surface((Log.BOX_WIDTH - Log.INSET_X * 2, line_height * Log.ROW_COUNT))
    log.surface.fill(COLOR_KEY)
    log.surface.set_colorkey(COLOR_KEY)
    if log.anim is None and log.dirty and (log.row >= len(log.cache) or log.cache[log.row]["dirty"]):
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
        log.anim = Anim(Log.EXIT_DURATION, {
          "kind": "exit",
          "target": log
        })

    if log.row >= Log.ROW_COUNT:
      log.offset += (log.row - 1 - log.offset) / 8

    for i in range(len(log.cache)):
      line = log.cache[i]
      y = round((i - log.offset) * line_height)
      log.surface.blit(line["surface"], (0, y))

    y = -log.box.get_height() - 8
    if log.anim is not None:
      t = log.anim.update()
      if log.anim.data["kind"] == "enter":
        t = ease_out(t)
      elif log.anim.data["kind"] == "exit":
        t = ease_in(1 - t)
      if log.anim.done:
        if log.anim.data["kind"] == "exit":
          log.messages = []
          log.cache = []
          log.row = -1
          log.offset = 0
        log.anim = None
      log.y = y * t
    elif log.row != -1 and (log.dirty or log.clean_frames < Log.HANG_DURATION):
      log.y = y
    else:
      log.y = 0

    log.box.blit(log.surface, (Log.INSET_X, Log.INSET_Y))
    return log.box
