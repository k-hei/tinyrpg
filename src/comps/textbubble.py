from math import sin, cos, pi
from pygame import Surface, SRCALPHA
from pygame.transform import scale
from assets import load as use_assets
from comps.textbox import TextBox
from comps.log import Message
from easing.circ import ease_out
from anims.tween import TweenAnim
from lib.lerp import lerp

class Bubble:
  def render(size):
    width, height = size
    sprites = use_assets().sprites
    surface = Surface(size, SRCALPHA)

    nw_image = sprites["bubble_nw"]
    n_image = sprites["bubble_n"]
    ne_image = sprites["bubble_ne"]
    w_image = sprites["bubble_w"]
    c_image = sprites["bubble_c"]
    e_image = sprites["bubble_e"]
    sw_image = sprites["bubble_sw"]
    s_image = sprites["bubble_s"]
    se_image = sprites["bubble_se"]

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
  PADDING_X = 12
  PADDING_Y = 16

  class EnterAnim(TweenAnim): pass
  class ResizeAnim(TweenAnim): pass

  def __init__(bubble, width, pos):
    bubble.width = width
    bubble.height = None
    bubble.pos = pos
    bubble.textbox = None
    bubble.anims = []
    bubble.ticks = 0

  def enter(bubble, on_end=None):
    bubble.anims.append(TextBubble.EnterAnim(
      duration=15,
      on_end=on_end
    ))

  def resize(bubble, height, on_end=None):
    def end():
      bubble.height = height
      on_end and on_end()
    bubble.anims.append(TextBubble.ResizeAnim(
      duration=10,
      target=height,
      on_end=end
    ))

  def print(bubble, token, on_end=None):
    textbox_width = bubble.width - TextBubble.PADDING_X * 2
    textbox_height = TextBox.height(token, textbox_width)
    entering = bubble.textbox is None
    resizing = not entering and textbox_height != bubble.height - TextBubble.PADDING_Y * 2
    start_print = lambda: bubble.textbox.print(token, on_end=on_end)
    if entering or resizing:
      bubble.textbox = TextBox((textbox_width, textbox_height))
      bubble_height = textbox_height + TextBubble.PADDING_Y * 2
      if entering:
        bubble.height = bubble_height
        bubble.enter(on_end=start_print)
      elif resizing:
        bubble.resize(bubble_height, on_end=start_print)
    else:
      start_print()

  def update(bubble):
    for anim in bubble.anims:
      if anim.done:
        bubble.anims.remove(anim)
      else:
        anim.update()
    bubble.ticks += 1

  def draw(bubble, surface):
    if bubble.textbox is None:
      return

    bubble.update()
    sprites = use_assets().sprites

    bubbletail_x, bubbletail_y = bubble.pos
    bubbletail_image = sprites["bubble_tail"]
    bubbletail_x -= bubbletail_image.get_width()
    bubbletail_y -= bubbletail_image.get_height() // 2
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
      elif type(bubble_anim) is TextBubble.ResizeAnim:
        t = ease_out(t)
        bubble_height = lerp(bubble_height, bubble_anim.target, t)
      bubble_widthoffset = 0
      bubble_heightoffset = 0
    else:
      bubble_widthoffset = sin(bubble.ticks % 90 / 90 * 2 * pi) * 2
      bubble_heightoffset = cos(bubble.ticks % 90 / 90 * 2 * pi) * 2
    bubble_image = Bubble.render((bubble_width + bubble_widthoffset, bubble_height + bubble_heightoffset))
    bubble_x, bubble_y = bubbletail_x, bubbletail_y
    bubble_x += -bubble_image.get_width() + 2
    bubble_y += bubbletail_image.get_height() // 2 - bubble_image.get_height() // 2
    bubble_xoffset = sin(bubble.ticks % 150 / 150 * 2 * pi) * 3
    bubble_yoffset = sin(bubble.ticks % 75 / 75 * 2 * pi) * 1.5

    surface.blit(bubble_image, (bubble_x + bubble_xoffset, bubble_y + bubble_yoffset))
    surface.blit(bubbletail_image, (bubbletail_x + bubble_xoffset, bubbletail_y + bubble_yoffset + bubbletail_offset))

    text_image = bubble.textbox.render()
    text_x = bubble_x + TextBubble.PADDING_X + bubble_widthoffset
    text_y = bubble_y + TextBubble.PADDING_Y + bubble_heightoffset // 2
    surface.blit(text_image, (text_x, text_y))
