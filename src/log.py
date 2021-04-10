from text import render as render_text
from pygame import Surface

COLOR_KEY = (0xFF, 0x00, 0XFF)

class Log:
  ROW_COUNT = 2

  def __init__(log):
    log.messages = []
    log.row = -1
    log.col = 0
    log.offset = 0
    log.dirty = False
    log.surface = Surface((288, 32))
    log.cache = []

  def print(log, message):
    log.messages.append(message)
    if not log.dirty:
      log.row += 1
      log.col = 0
      log.dirty = True

  def render(log, font):
    log.surface.fill(COLOR_KEY)
    log.surface.set_colorkey(COLOR_KEY)
    if log.dirty and (log.row >= len(log.cache) or log.cache[log.row]["dirty"]):
      if log.row >= len(log.cache):
        surface = Surface((log.surface.get_width(), font.char_height + font.line_spacing))
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

    if log.row >= Log.ROW_COUNT:
      log.offset += (log.row - 1 - log.offset) / 8

    for i in range(len(log.cache)):
      line = log.cache[i]
      y = round((i - log.offset) * (font.char_height + font.line_spacing))
      log.surface.blit(line["surface"], (0, y))

    return log.surface
