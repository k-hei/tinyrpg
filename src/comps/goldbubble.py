from pygame import Surface, SRCALPHA
from lib.sprite import Sprite
import lib.vector as vector
import assets
from comps.box import Box
from anims.tween import TweenAnim
from colors.palette import WHITE, GRAY, RED, CYAN

DIGITS = 4
VALUE_XPADDING = 6
VALUE_YPADDING = 9
DELTA_XPADDING = 6
DELTA_YPADDING = 4
DELTA_OVERLAP = 7

def render_gold(gold, color=WHITE):
  bubble_surface = assets.sprites["bubble_gold"].copy()
  prefix_image = assets.ttf["english"].render("0" * (DIGITS - len(str(gold))), GRAY)
  value_image = assets.ttf["english"].render(str(gold), color)
  value_surface = Surface((prefix_image.get_width() + value_image.get_width(), prefix_image.get_height()), flags=SRCALPHA)
  value_surface.blit(prefix_image, (0, 0))
  value_surface.blit(value_image, (prefix_image.get_width(), 0))
  bubble_surface.blit(value_surface, (bubble_surface.get_width() - value_surface.get_width() - VALUE_XPADDING, VALUE_YPADDING))
  return bubble_surface

def render_delta(delta, t=1):
  delta_color = (
    delta == 0 and WHITE
    or delta < 0 and RED
    or delta > 0 and CYAN
  )
  delta_symbol = "+" if delta >= 0 else ""
  delta_text = delta_symbol + str(delta)
  delta_width = assets.ttf["english"].width(delta_text) + DELTA_XPADDING * 2
  delta_height = 16
  if t == 1:
    delta_image = assets.ttf["english"].render(text=delta_text, color=delta_color)
  else:
    delta_image = None
    delta_width = int(delta_width * t)
    delta_height = int(delta_height * t)
  bubble_surface = Box(
    sprite_prefix="box_delta",
    size=(delta_width, delta_height)
  ).render()
  if delta_image:
    bubble_surface.blit(delta_image, (bubble_surface.get_width() - delta_image.get_width() - DELTA_XPADDING, DELTA_YPADDING))
  return bubble_surface

class GoldBubble:
  class DeltaAnim(TweenAnim): duration = 15
  class DeltaEnterAnim(DeltaAnim): duration = 15
  class DeltaExitAnim(DeltaAnim): duration = 7

  def __init__(bubble, gold=0, pos=(0, 0)):
    bubble.anims = []
    bubble.gold = gold
    bubble.gold_drawn = gold
    bubble.pos = pos
    bubble.pos_drawn = pos
    bubble.delta = 0
    bubble.changing = False

  @property
  def gold(bubble):
    return bubble._gold

  @gold.setter
  def gold(bubble, gold):
    if "_gold" in dir(bubble) and bubble._gold != gold:
      bubble.changing = True
    bubble._gold = gold

  @property
  def delta(bubble):
    return bubble._delta

  @delta.setter
  def delta(bubble, delta):
    if "_delta" in dir(bubble):
      if delta == 0:
        bubble.changing = False
        bubble.anims.append(GoldBubble.DeltaExitAnim(target=bubble._delta))
      elif bubble._delta == 0:
        bubble.anims.append(GoldBubble.DeltaEnterAnim())
    bubble._delta = delta

  def update(bubble):
    bubble.anims = [(a.update(), a)[-1] for a in bubble.anims if not a.done]

  def view(bubble):
    bubble.update()
    sprites = []

    old_gold_drawn = bubble.gold_drawn
    bubble.gold_drawn += (bubble.gold - bubble.gold_drawn) / 16
    if round(bubble.gold_drawn) == bubble.gold and round(old_gold_drawn) != bubble.gold:
      bubble.delta = 0

    if -bubble.delta > bubble.gold_drawn and not bubble.changing:
      value_color = RED
    else:
      value_color = WHITE

    bubble.pos_drawn = vector.add(bubble.pos_drawn, vector.scale(vector.subtract(bubble.pos, bubble.pos_drawn), 1 / 8))
    sprites += [bubble_sprite := Sprite(
      image=render_gold(round(bubble.gold_drawn), color=value_color),
      pos=bubble.pos_drawn,
      origin=Sprite.ORIGIN_LEFT
    )]

    delta_anim = next((a for a in bubble.anims if isinstance(a, GoldBubble.DeltaAnim)), None)
    if bubble.delta or delta_anim:
      delta_value = bubble.delta
      if type(delta_anim) is GoldBubble.DeltaEnterAnim:
        t = delta_anim.pos
      elif type(delta_anim) is GoldBubble.DeltaExitAnim:
        t = 1 - delta_anim.pos
        delta_value = delta_anim.target
      else:
        t = 1
      sprites += [delta_sprite := Sprite(
        image=render_delta(delta_value, t),
        pos=vector.add(
          bubble_sprite.rect.bottomright,
          (0, -DELTA_OVERLAP)
        ),
        origin=Sprite.ORIGIN_TOPRIGHT
      )]

    return sprites
