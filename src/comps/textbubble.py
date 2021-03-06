from math import sin, cos, pi
import pygame
from pygame import Surface, SRCALPHA
from pygame.transform import scale, flip, rotate
from lib.filters import replace_color
import lib.keyboard as keyboard
import lib.input as input
import lib.vector as vector

from assets import assets
from comps.textbox import TextBox
from comps.log import Message
from contexts import Context
from contexts.choice import Choice # used as export
from easing.circ import ease_out
from anims.tween import TweenAnim
from anims.sine import SineAnim
from anims.flicker import FlickerAnim
from lib.lerp import lerp
from lib.sprite import Sprite
from colors.palette import BLACK, WHITE, RED

def invert(image):
  inverse = replace_color(image, WHITE, RED)
  inverse = replace_color(inverse, BLACK, WHITE)
  inverse = replace_color(inverse, RED, BLACK)
  return inverse

BUBBLE_SPRITEIDS = [
  "bubble_nw",
  "bubble_n",
  "bubble_ne",
  "bubble_w",
  "bubble_c",
  "bubble_e",
  "bubble_sw",
  "bubble_s",
  "bubble_se",
  "bubble_tail"
]

for spriteid in BUBBLE_SPRITEIDS:
  assets.sprites[f"{spriteid}_inverse"] = invert(assets.sprites[spriteid])

class Bubble:
  def render(size, inverse=False):
    width, height = size
    images = assets.sprites
    surface = Surface(size, SRCALPHA)

    nw_image = images["bubble_nw"] if not inverse else images["bubble_nw_inverse"]
    n_image = images["bubble_n"] if not inverse else images["bubble_n_inverse"]
    ne_image = images["bubble_ne"] if not inverse else images["bubble_ne_inverse"]
    w_image = images["bubble_w"] if not inverse else images["bubble_w_inverse"]
    c_image = images["bubble_c"] if not inverse else images["bubble_c_inverse"]
    e_image = images["bubble_e"] if not inverse else images["bubble_e_inverse"]
    sw_image = images["bubble_sw"] if not inverse else images["bubble_sw_inverse"]
    s_image = images["bubble_s"] if not inverse else images["bubble_s_inverse"]
    se_image = images["bubble_se"] if not inverse else images["bubble_se_inverse"]

    n_width = int(width - nw_image.get_width() - ne_image.get_width())
    n_height = n_image.get_height()
    if n_width > 0:
      surface.blit(scale(n_image, (n_width, n_height)), (nw_image.get_width(), 0))

    w_width = w_image.get_width()
    w_height = int(height - nw_image.get_height() - sw_image.get_height())
    if w_height > 0:
      surface.blit(scale(w_image, (w_width, w_height)), (0, nw_image.get_height()))

    s_width = int(width - sw_image.get_width() - se_image.get_width())
    s_height = s_image.get_height()
    if s_width > 0:
      surface.blit(scale(s_image, (s_width, s_height)), (sw_image.get_width(), height - s_height))

    e_width = e_image.get_width()
    e_height = int(height - ne_image.get_height() - se_image.get_height())
    if e_height > 0:
      surface.blit(scale(e_image, (e_width, e_height)), (width - e_width, ne_image.get_height()))

    if n_width > 0 and w_height > 0:
      surface.blit(scale(c_image, (n_width, w_height)), n_image.get_size())

    surface.blit(nw_image, (0, 0))
    surface.blit(ne_image, (width - ne_image.get_width(), 0))
    surface.blit(sw_image, (0, height - sw_image.get_height()))
    surface.blit(se_image, (width - se_image.get_width(), height - se_image.get_height()))

    return surface

class TextBubble:
  XPADDING = 12

  class EnterAnim(TweenAnim): pass
  class ExitAnim(TweenAnim): pass
  class ResizeAnim(TweenAnim): pass

  class PromptContext(Context):
    def __init__(ctx, choices, required=False, *args, **kwargs):
      super().__init__(*args, **kwargs)
      ctx.choices = choices
      ctx.choice_index = 0
      ctx.choice = None
      ctx.cursor_anim = SineAnim(period=30, amplitude=2)
      ctx.anims = []

    def handle_press(ctx, button):
      if ctx.anims:
        return False

      if input.get_state(button) > 1:
        return

      controls = input.resolve_controls(button)
      button = input.resolve_button(button)

      if button == input.BUTTON_LEFT:
        return ctx.handle_move(delta=-1)

      if button == input.BUTTON_RIGHT:
        return ctx.handle_move(delta=1)

      if input.CONTROL_CONFIRM in controls:
        return ctx.handle_choose()

      if input.CONTROL_CANCEL in controls:
        return ctx.handle_cancel()

    def handle_move(ctx, delta):
      old_index = ctx.choice_index
      new_index = old_index + delta
      if new_index < 0:
        new_index = 0
        return False
      elif new_index > len(ctx.choices) - 1:
        new_index = len(ctx.choices) - 1
        return False
      ctx.choice_index = new_index
      return True

    def handle_choose(ctx):
      choice = ctx.choices[ctx.choice_index]
      if choice.closing:
        ctx.close(choice)
      else:
        ctx.anims.append(FlickerAnim(
          duration=30,
          target=choice,
          on_end=lambda: ctx.close(choice)
        ))
      ctx.choice = choice
      return True

    def handle_cancel(ctx):
      ctx.close(None)

    def update(ctx):
      for anim in ctx.anims:
        if anim.done:
          ctx.anims.remove(anim)
        else:
          anim.update()

    def view(ctx):
      sprites = []
      font = assets.ttf["english"]
      choices_width = 0
      choices_height = font.height()
      choices_xs = {}
      for i, choice in enumerate(ctx.choices):
        if choices_width:
          choices_width += 12
        choices_xs[i] = choices_width
        choices_width += font.width(choice.text)
      choices_image = Surface((choices_width, choices_height), SRCALPHA)
      for i, choice in enumerate(ctx.choices):
        choice_anim = next((a for a in ctx.anims if a.target is choice), None)
        if choice_anim and not choice_anim.visible:
          continue
        choice_image = font.render(choice.text, color=BLACK)
        choices_image.blit(choice_image, (choices_xs[i], 0))
      sprites.append(Sprite(
        image=choices_image,
        pos=(0, 0)
      ))
      cursor_x = choices_xs[ctx.choice_index] + ctx.cursor_anim.update()
      sprites.append(Sprite(
        image=flip(assets.sprites["hand"], True, False),
        pos=(cursor_x, choices_height // 2),
        origin=("right", "center")
      ))
      return sprites

  def __init__(bubble, width=0, pos=(0, 0), origin=Sprite.ORIGIN_RIGHT, offset=(0, 0), inverse=False, flip_tail=False, ypadding=16):
    bubble.width = width
    bubble.height = 0
    bubble.offset_height = 0
    bubble.pos = pos
    bubble.origin = origin
    bubble.offset = offset
    bubble.inverse = inverse
    bubble.flip_tail = flip_tail
    bubble.ypadding = ypadding
    bubble.textbox = None
    bubble.anims = []
    bubble.ctx = None
    bubble.message = None
    bubble.printing = False
    bubble.exiting = False
    bubble.ticks = 0

  @property
  def is_entering(bubble):
    return bubble.textbox is None

  @property
  def is_resizing(bubble):
    return not bubble.is_entering and bubble.height - bubble.ypadding * 2 != bubble.textbox_height

  @property
  def textbox_width(bubble):
    return bubble.width - TextBubble.XPADDING * 2

  @property
  def textbox_height(bubble):
    return TextBox.height(bubble.message, bubble.textbox_width) + bubble.offset_height

  def enter(bubble, on_end=None):
    bubble.anims.append(
      TextBubble.EnterAnim(duration=15, on_end=on_end)
    )

  def exit(bubble, on_end=None):
    bubble.exiting = True
    bubble.textbox.clear()
    bubble.anims.append(
      TextBubble.ExitAnim(duration=8, on_end=on_end)
    )

  def resize(bubble, height, on_end=None):
    bubble.anims.append(TextBubble.ResizeAnim(
      duration=10,
      target=(bubble.height, height),
      on_end=on_end
    ))
    bubble.height = height

  def print(bubble, message, offset_height=0, on_end=None):
    bubble.message = message
    bubble.offset_height = offset_height

    def end_print():
      bubble.printing = False
      on_end and on_end()

    def start_print():
      bubble.printing = True
      bubble.textbox.print(message, on_end=end_print)

    if bubble.is_entering or bubble.is_resizing:
      bubble.width = bubble.width or (assets.ttf["normal"].width(str(Message(message))) + TextBubble.XPADDING * 2)
      bubble.textbox = TextBox((bubble.textbox_width, bubble.textbox_height), color=BLACK if not bubble.inverse else WHITE)
      bubble_height = bubble.textbox_height + bubble.ypadding * 2
      if bubble.is_entering:
        bubble.height = bubble_height
        bubble.enter(on_end=start_print)
      elif bubble.is_resizing:
        bubble.resize(bubble_height, on_end=start_print)
    else:
      start_print()

  def prompt(bubble, message, choices=[], on_choose=None, on_close=None):
    bubble.print(message, offset_height=16)
    def handle_close(choice):
      bubble.ctx = None
      return choice
    bubble.ctx = TextBubble.PromptContext(choices, on_close=handle_close)
    return bubble.ctx

  def update(bubble):
    for anim in bubble.anims:
      if anim.done:
        bubble.anims.remove(anim)
      else:
        anim.update()
    bubble.ticks += 1

  def view(bubble):
    if bubble.textbox is None:
      return []

    bubble.update()
    sprites = []

    bubbletail_x, bubbletail_y = bubble.pos
    bubbletail_image = assets.sprites["bubble_tail"] if not bubble.inverse else assets.sprites["bubble_tail_inverse"]

    if bubble.origin == Sprite.ORIGIN_RIGHT:
      bubbletail_x -= bubbletail_image.get_width()
      bubbletail_y -= bubbletail_image.get_height() // 2
      if bubble.flip_tail:
        bubbletail_image = flip(bubbletail_image, False, True)

    if bubble.origin == Sprite.ORIGIN_TOP:
      bubbletail_image = rotate(bubbletail_image, 90)
      bubbletail_x -= bubbletail_image.get_width() // 2
      if bubble.flip_tail:
        bubbletail_image = flip(bubbletail_image, True, False)

    if bubble.origin == Sprite.ORIGIN_LEFT:
      bubbletail_image = rotate(bubbletail_image, 180)
      bubbletail_y -= bubbletail_image.get_height() // 2
      if bubble.flip_tail:
        bubbletail_image = flip(bubbletail_image, False, True)

    bubbletail_offset = cos(bubble.ticks % 75 / 75 * 2 * pi)

    bubble_width = bubble.width
    bubble_height = bubble.height
    bubble_anim = next((a for a in bubble.anims if a), None)
    if bubble_anim:
      t = bubble_anim.pos
      if type(bubble_anim) is TextBubble.EnterAnim:
        t = ease_out(t)
        bubble_width *= t
        bubble_height *= t
      elif type(bubble_anim) is TextBubble.ExitAnim:
        t = 1 - t
        bubble_width *= t
        bubble_height *= t
      elif type(bubble_anim) is TextBubble.ResizeAnim:
        start_height, goal_height = bubble_anim.target
        t = ease_out(t)
        bubble_height = lerp(start_height, goal_height, t)
      bubble_widthoffset = 0
      bubble_heightoffset = 0
    else:
      bubble_widthoffset = sin(bubble.ticks % 90 / 90 * 2 * pi) * 2
      bubble_heightoffset = cos(bubble.ticks % 90 / 90 * 2 * pi) * 2
    bubble_image = Bubble.render(
      size=(bubble_width + bubble_widthoffset, bubble_height + bubble_heightoffset),
      inverse=bubble.inverse
    )
    bubble_x, bubble_y = vector.subtract((bubbletail_x, bubbletail_y), bubble.offset)

    if bubble.origin == Sprite.ORIGIN_RIGHT:
      bubble_x += -bubble_image.get_width() + 2
      bubble_y += bubbletail_image.get_height() // 2 - bubble_image.get_height() // 2
      bubbletail_xoffset = 0
      bubbletail_yoffset = bubbletail_offset
      text_xoffset = bubble_widthoffset
      text_yoffset = bubble_heightoffset // 2

    if bubble.origin == Sprite.ORIGIN_TOP:
      bubble_x += bubbletail_image.get_width() // 2 - bubble_image.get_width() // 2
      bubble_y += bubbletail_image.get_height() // 2 + 2
      bubbletail_xoffset = bubbletail_offset
      bubbletail_yoffset = 0
      text_xoffset = bubble_widthoffset // 2
      text_yoffset = 0

    if bubble.origin == Sprite.ORIGIN_LEFT:
      bubble_x += bubbletail_image.get_width() // 2 + 2
      bubble_y += bubbletail_image.get_height() // 2 - bubble_image.get_height() // 2
      bubbletail_xoffset = 0
      bubbletail_yoffset = bubbletail_offset
      text_xoffset = 0
      text_yoffset = bubble_heightoffset // 2

    bubble_xoffset = sin(bubble.ticks % 150 / 150 * 2 * pi) * 3
    bubble_yoffset = sin(bubble.ticks % 75 / 75 * 2 * pi) * 1.5

    if bubble_anim or not bubble.exiting:
      sprites.append(Sprite(
        image=bubble_image,
        pos=(bubble_x + bubble_xoffset, bubble_y + bubble_yoffset)
      ))
      if bubble_width and bubble_height:
        sprites.append(Sprite(
          image=bubbletail_image,
          pos=(bubbletail_x + bubble_xoffset + bubbletail_xoffset, bubbletail_y + bubble_yoffset + bubbletail_yoffset
        )))
      if not bubble.exiting:
        text_image = bubble.textbox.render()
        text_x = bubble_x + TextBubble.XPADDING + text_xoffset
        text_y = bubble_y + bubble.ypadding + text_yoffset
        sprites.append(Sprite(
          image=text_image,
          pos=(text_x, text_y)
        ))

    if bubble.ctx and not bubble_anim and not bubble.printing:
      choices_x = text_x + bubble_width - TextBubble.XPADDING * 2
      choices_y = text_y + bubble_height - bubble.ypadding * 2
      choices_view = bubble.ctx.view()
      choices_image = choices_view and choices_view[0].image
      for sprite in choices_view:
        sprite.move((choices_x - choices_image.get_width(), choices_y - choices_image.get_height()))
      sprites += choices_view

    return sprites
