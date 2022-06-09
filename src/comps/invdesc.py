from pygame import Surface, Rect, SRCALPHA
from easing.expo import ease_out
from lib.lerp import lerp
from anims.tween import TweenAnim
import assets
from items import Item
from comps.log import Message, Token
from comps.textbox import TextBox

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
    box.textbox = TextBox((
      assets.sprites["item_desc"].get_width() - PADDING_LEFT - PADDING_RIGHT,
      assets.sprites["item_desc"].get_height() - PADDING_Y * 2
    ))
    box.index = 0
    box.cursor = (0, 0)
    box.anim = None
    box.active = True

  def enter(box):
    box.active = True
    box.anim = TweenAnim(duration=DURATION_ENTER)

  def exit(box):
    box.active = False
    box.anim = TweenAnim(duration=DURATION_EXIT)

  def print(box, data):
    if isinstance(data, type) and issubclass(data, Item) or isinstance(data, Item):
      box.message = data
      box.textbox.print(data.desc)
    else:
      box.message = Message(data)
      box.textbox.print(data)

  def render(box):
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
      text_image = box.textbox.render()
      if type(box.message) is Message:
        surface.blit(text_image, (PADDING_LEFT, PADDING_Y))
      else:
        item = box.message
        title_image = font_heading.render(item.name, item.color)
        surface.blit(title_image, (PADDING_LEFT, PADDING_Y))
        surface.blit(text_image, (PADDING_LEFT, PADDING_Y + title_image.get_height() + TITLE_SPACING))
      return surface
    elif box.active:
      return surface
    else:
      return None
