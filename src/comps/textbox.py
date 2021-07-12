from pygame import Surface, SRCALPHA
from assets import load as use_assets
from comps.log import Message
from colors.palette import BLACK

LINE_SPACING = 4

class TextBox:
  font = "roman"

  def height(token, width):
    assets = use_assets()
    font = assets.ttf[TextBox.font]
    index = 0
    cursor_x, cursor_y = (0, 0)
    message = Message(token)
    while index < len(message):
      char = message[index]
      if char == "\n":
        cursor_x = 0
        cursor_y += font.height() + LINE_SPACING
        index += 1
      if index == 0 or char in (" ", "\n"):
        next_space = message.find(" ", index + 1)
        if next_space == -1:
          next_space = message.find("\n", index + 1)
        if next_space == -1:
          word = message[index+1:]
        else:
          word = message[index+1:next_space]
        word_width, word_height = font.size(word)
        space_width, _ = font.size(" ")
        if cursor_x + space_width + word_width > width:
          cursor_x = 0
          cursor_y += word_height + LINE_SPACING
          index += 1
      char = message[index]
      cursor_x += font.width(char)
      index += 1
    return cursor_y + font.height()

  def __init__(box, size, font=None, color=BLACK):
    box.size = size
    box.font = font or TextBox.font
    box.color = color
    box.message = None
    box.on_print = None
    box.index = 0
    box.cursor = (0, 0)
    box.surface = None

  def print(box, token, on_end=None):
    message = Message(token)
    if box.message and str(message) == str(box.message):
      return
    box.clear()
    box.message = message
    box.on_print = on_end

  def clear(box):
    box.index = 0
    box.cursor = (0, 0)
    box.surface = None

  def render(box):
    assets = use_assets()
    font = assets.ttf[box.font]
    if box.surface is None:
      box.surface = Surface(box.size, SRCALPHA)
    if box.message is None:
      return box.surface
    if box.index < len(box.message):
      cursor_x, cursor_y = box.cursor
      char = box.message[box.index]
      if char == "\n":
        cursor_x = 0
        cursor_y += font.height() + LINE_SPACING
        box.index += 1
      if box.index == 0 or char in (" ", "\n"):
        next_space = box.message.find(" ", box.index + 1)
        if next_space == -1:
          next_space = box.message.find("\n", box.index + 1)
        if next_space == -1:
          word = box.message[box.index+1:]
        else:
          word = box.message[box.index+1:next_space]
        word_width, word_height = font.size(word)
        space_width, _ = font.size(" ")
        if cursor_x + space_width + word_width > box.surface.get_width():
          cursor_x = 0
          cursor_y += word_height + LINE_SPACING
          box.index += 1
      char = box.message[box.index]
      token = box.message.get_token_at(box.index) if type(box.message) is Message else None
      color = token and token.color or box.color
      char_image = font.render(char, color)
      box.surface.blit(char_image, (cursor_x, cursor_y))
      cursor_x += char_image.get_width()
      box.index += 1
      box.cursor = (cursor_x, cursor_y)
    if box.index == len(box.message) and box.on_print:
      box.on_print()
      box.on_print = None
    return box.surface
