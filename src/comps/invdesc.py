from pygame import Surface, Rect, SRCALPHA
from anims.tween import TweenAnim
from easing.expo import ease_out
from lib.lerp import lerp
from assets import load as use_assets
from comps.log import Message, Token

PADDING_LEFT = 12
PADDING_RIGHT = 12
PADDING_Y = 10
TITLE_SPACING = 5
WORD_SPACING = 8
LINE_SPACING = 3
DURATION_ENTER = 15
DURATION_EXIT = 7

class InventoryDescription:
  def __init__(box):
    box.message = None
    box.index = 0
    box.cursor = (0, 0)
    box.surface = None
    box.anim = None
    box.active = True

  def enter(box):
    box.active = True
    box.anim = TweenAnim(duration=DURATION_ENTER)

  def exit(box):
    box.active = False
    box.anim = TweenAnim(duration=DURATION_EXIT)

  def print(box, data):
    box.clear()
    if type(data) is str or type(data) is tuple:
      box.message = Message(data)
    else:
      box.message = data

  def clear(box):
    box.index = 0
    box.cursor = (0, 0)
    box.surface = None

  def render(box):
    assets = use_assets()
    font_heading = assets.ttf["english"]
    font_content = assets.ttf["normal"]
    surface = assets.sprites["item_desc"].copy()
    if box.anim:
      t = box.anim.update()
      if box.anim.done:
        box.anim = None
      if box.active:
        t = ease_out(t)
      else:
        t = 1 - t
      start_height = 0
      end_height = surface.get_height()
      sprite_height = lerp(start_height, end_height, t)
      return surface.subsurface(Rect(
        (0, 0),
        (surface.get_width(), sprite_height)
      ))
    elif box.active and box.message:
      if box.surface is None:
        box.surface = Surface((
          surface.get_width() - PADDING_LEFT - PADDING_RIGHT,
          surface.get_height() - PADDING_Y * 2
        ), SRCALPHA)

      if type(box.message) is Message:
        sprite_title = None
        message = box.message
      else:
        item = box.message
        sprite_title = font_heading.render(item.name, item.color)
        message = item.desc

      if box.index < len(message):
        cursor_x, cursor_y = box.cursor
        char = message[box.index]
        if char == "\n":
          cursor_x = 0
          cursor_y += font_content.height() + LINE_SPACING
          box.index += 1
        if box.index == 0 or char in (" ", "\n"):
          next_space = message.find(" ", box.index + 1)
          if next_space == -1:
            next_space = message.find("\n", box.index + 1)
          if next_space == -1:
            word = message[box.index+1:]
          else:
            word = message[box.index+1:next_space]
          word_width, word_height = font_content.size(word)
          space_width, _ = font_content.size(" ")
          if cursor_x + space_width + word_width > box.surface.get_width():
            cursor_x = 0
            cursor_y += word_height + LINE_SPACING
            box.index += 1
        char = message[box.index]
        token = message.get_token_at(box.index) if type(message) is Message else None
        color = token and token.color or 0
        sprite_char = font_content.render(char, color)
        box.surface.blit(sprite_char, (cursor_x, cursor_y))
        cursor_x += sprite_char.get_width()
        box.index += 1
        box.cursor = (cursor_x, cursor_y)

      if sprite_title:
        surface.blit(sprite_title, (PADDING_LEFT, PADDING_Y))
        surface.blit(box.surface, (PADDING_LEFT, PADDING_Y + sprite_title.get_height() + TITLE_SPACING))
      else:
        surface.blit(box.surface, (PADDING_LEFT, PADDING_Y))
      return surface
    elif box.active:
      return surface
    else:
      return None
