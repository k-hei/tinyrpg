import pygame
from pygame import Surface, Rect, Color, SRCALPHA
from lib.lerp import lerp
from easing.expo import ease_in, ease_out

import assets
from comps import Component
from anims.tween import TweenAnim
from sprite import Sprite
from lib.filters import outline, shadow
from colors.palette import WHITE, BLUE

BG_Y = 24
BG_WIDTH = 168
BG_HEIGHT = 16
CHAR_FONT = "roman_large"

def get_char_spacing(old_char, new_char):
  if old_char == " ": return -10
  if old_char == "A" and new_char == "V": return -7
  if old_char == "A" and new_char == "T": return -7
  if old_char == "T" and new_char == "A": return -6
  return -4

class CharAnim(TweenAnim): pass
class CharEnterAnim(CharAnim): pass
class CharExitAnim(CharAnim): pass
class BgAnim(TweenAnim): pass
class BgEnterAnim(BgAnim): pass
class BgExitAnim(BgAnim): pass

class Title(Component):
  def __init__(title, text, color=BLUE):
    super().__init__()
    title.text = text
    title.anims = []
    title.cache_bg = None
    title.cache_chars = {}

  def enter(title):
    super().enter()
    title.anims.append(BgEnterAnim(duration=20))
    for i, char in enumerate(title.text):
      title.anims.append(CharEnterAnim(
        duration=7,
        delay=i * 2,
        target=i
      ))

  def exit(title, on_end=None):
    super().exit()
    title.anims.append(BgExitAnim(
      duration=10,
      delay=15,
      on_end=on_end
    ))
    for i, char in enumerate(title.text):
      title.anims.append(CharExitAnim(
        duration=7,
        delay=i * 2,
        target=i
      ))

  def update(title):
    for anim in title.anims:
      if anim.done:
        title.anims.remove(anim)
      else:
        anim.update()

  def view(title):
    sprites = []

    # title bg
    bg_anim = next((a for a in title.anims if isinstance(a, BgAnim)), None)
    bg_width = BG_WIDTH
    if type(bg_anim) is BgEnterAnim:
      bg_width *= ease_out(bg_anim.pos)
    elif type(bg_anim) is BgExitAnim:
      bg_width *= 1 - ease_in(bg_anim.pos)
    elif not title.active:
      bg_width = 0
    if bg_width:
      if not title.cache_bg:
        title.cache_bg = Surface((BG_WIDTH, BG_HEIGHT), flags=SRCALPHA)
      title.cache_bg.fill(Color(0, 0, 0, 0))
      pygame.draw.rect(title.cache_bg, BLUE, Rect(0, 0, bg_width, BG_HEIGHT))
      sprites.append(Sprite(
        image=title.cache_bg,
        pos=(0, BG_Y)
      ))

    # title text
    char_anims = [a for a in title.anims if isinstance(a, CharAnim)]
    x = 16
    for i, char in enumerate(title.text):
      anim = next((a for a in char_anims if a.target == i), None)
      if char not in title.cache_chars:
        title.cache_chars[char] = render_char(char)
      char_image = title.cache_chars[char]
      from_y = -char_image.get_height()
      to_y = 16
      if type(anim) is CharEnterAnim:
        t = ease_out(anim.pos)
        y = lerp(from_y, to_y, t)
      elif type(anim) is CharExitAnim:
        t = ease_in(anim.pos)
        y = lerp(to_y, from_y, t)
      elif title.active:
        y = to_y
      else:
        y = None
      if y is not None:
        sprites.append(Sprite(
          image=char_image,
          pos=(x, y),
          offset=32
        ))
      if i + 1 < len(title.text):
        x += char_image.get_width() + get_char_spacing(char, title.text[i + 1])

    return sprites

def render_char(char):
  char_image = assets.ttf[CHAR_FONT].render(char)
  char_image = outline(char_image, BLUE)
  char_image = shadow(char_image, BLUE)
  char_image = outline(char_image, WHITE)
  return char_image
