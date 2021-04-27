from pygame import Surface, Rect
from anims.tween import TweenAnim
from easing.expo import ease_out
from lerp import lerp
from assets import load as use_assets
from items import get_color

PADDING_X = 12
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

  def print(box, message):
    box.clear()
    box.message = message

  def clear(box):
    box.index = 0
    box.cursor = (0, 0)
    box.surface = None

  def render(box):
    assets = use_assets()
    font_heading = assets.ttf["english"]
    font_content = assets.ttf["roman"]
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
          surface.get_width() - PADDING_X * 2,
          surface.get_height() - PADDING_Y * 2
        )).convert_alpha()

      if type(box.message) is str:
        sprite_title = None
        message = box.message
      else:
        # assume message is an Item (TODO: item superclass)
        item = box.message
        sprite_title = font_heading.render(item.name, get_color(item))
        message = item.desc

      if box.index < len(message):
        cursor_x, cursor_y = box.cursor
        if box.index == 0 or message[box.index] == " ":
          next_space = message.find(" ", box.index + 1)
          if next_space == -1:
            word = message[box.index+1:]
          else:
            word = message[box.index+1:next_space]
          word_width, word_height = font_content.size(word)
          if cursor_x + word_width > box.surface.get_width():
            cursor_x = 0
            cursor_y += word_height + LINE_SPACING
            box.index += 1
        char = message[box.index]
        sprite_char = font_content.render(char, 0x000000)
        box.surface.blit(sprite_char, (cursor_x, cursor_y))
        cursor_x += sprite_char.get_width()
        box.index += 1
        box.cursor = (cursor_x, cursor_y)

      if sprite_title:
        surface.blit(sprite_title, (PADDING_X, PADDING_Y))
        surface.blit(box.surface, (PADDING_X, PADDING_Y + sprite_title.get_height() + TITLE_SPACING))
      else:
        surface.blit(box.surface, (PADDING_X, PADDING_Y))
      return surface
    elif box.active:
      return surface
    else:
      return None
