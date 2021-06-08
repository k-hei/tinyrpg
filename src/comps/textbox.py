from pygame import Surface, SRCALPHA
from assets import load as use_assets
from comps.log import Message

LINE_SPACING = 4

class Textbox:
  def __init__(box, size, font="roman"):
    box.size = size
    box.font = font
    box.message = None
    box.index = 0
    box.cursor = (0, 0)
    box.surface = None

  def print(box, data):
    box.clear()
    box.message = Message(data)

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
      color = token and token.color or 0
      char_image = font.render(char, color)
      box.surface.blit(char_image, (cursor_x, cursor_y))
      cursor_x += char_image.get_width()
      box.index += 1
      box.cursor = (cursor_x, cursor_y)
    return box.surface
