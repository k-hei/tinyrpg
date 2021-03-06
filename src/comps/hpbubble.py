from math import ceil
from random import randint
from pygame import Rect
from comps import Component
import assets
from lib.sprite import Sprite
from lib.filters import replace_color
from colors.palette import WHITE, RED
from anims import Anim

DEPLETE_SPEED = 0.25

class HpBubble(Component):
  def __init__(bubble, actor, color=RED):
    bubble.actor = actor
    bubble.hp = actor.hp
    bubble.anim = None
    bubble.offset = None
    bubble.color = color

  def update(bubble):
    if bubble.anim and not bubble.anim.done:
      bubble.anim.update()

  def view(bubble):
    if bubble.actor.hp >= bubble.actor.hp_max:
      return []

    sprites = [Sprite(
      image=replace_color(assets.sprites["hpbubble"], WHITE, bubble.color),
      origin=Sprite.ORIGIN_BOTTOM,
      layer="vfx"
    )]

    if bubble.actor.hp < bubble.hp:
      if abs(bubble.actor.hp - bubble.hp) <= DEPLETE_SPEED:
        bubble.hp = bubble.actor.hp
      else:
        bubble.hp -= DEPLETE_SPEED
      if bubble.anim == None or bubble.actor.hp != bubble.anim.target:
        bubble.anim = Anim(duration=12, target=bubble.actor.hp)

    if bubble.hp != bubble.actor.hp:
      sprites.append(render_bubblefill(
        value=min(1, bubble.hp / bubble.actor.hp_max),
        color=WHITE
      ))

    if bubble.hp:
      sprites.append(render_bubblefill(
        value=min(1, bubble.actor.hp / bubble.actor.hp_max),
        color=bubble.color
      ))

    bubble.update()
    if bubble.anim and not bubble.anim.done:
      offset = bubble.offset
      while offset == bubble.offset:
        offset = (randint(-1, 1), randint(-1, 1))
      bubble.offset = offset
      for sprite in sprites:
        sprite.move(bubble.offset)

    return sprites

def render_bubblefill(value, color=WHITE):
  fill_image = assets.sprites["hpbubble_fill"]
  if color != WHITE:
    fill_image = replace_color(fill_image, WHITE, color)
  fill_height = ceil(value * fill_image.get_height())
  fill_image = fill_image.subsurface(Rect(
    (0, fill_image.get_height() - fill_height),
    (fill_image.get_width(), fill_height)
  ))
  return Sprite(
    image=fill_image,
    pos=(0, -5),
    offset=32,
    origin=Sprite.ORIGIN_BOTTOM,
    layer="vfx"
  )
