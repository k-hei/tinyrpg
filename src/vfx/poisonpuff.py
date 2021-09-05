from math import sin, pi
from random import random, randint
from lib.cell import add as add_vector
from easing.circ import ease_out
from vfx import Vfx
import assets
from sprite import Sprite
from anims import Anim
from anims.flicker import FlickerAnim
from anims.offsetmove import OffsetMoveAnim
from filters import replace_color
from colors.palette import WHITE, BLACK, VIOLET, DARKBLUE
from config import TILE_SIZE

class PoisonPuffVfx(Vfx):
  class FloatAnim(Anim): pass

  def __init__(puff, src, dest, size, *args, **kwargs):
    super().__init__(kind=None, pos=(0, 0), *args, **kwargs)
    puff.size = size
    puff.anims = [
      PoisonPuffVfx.FloatAnim(),
      OffsetMoveAnim(src, dest, speed=(2 + random()) * TILE_SIZE, easing=ease_out)
    ]
    puff.flickering = size != "large" and randint(1, 3) == 1
    puff.offset = tuple([(random() - 0.5) * 16 for i in range(2)])
    puff.offset_period = random() * 5
    puff.offset_amplitude = random() * 7
    puff.offset_direction = randint(0, 1) * 2 - 1
    puff.offset_axis = randint(0, 1)
    puff.update()

  def dissolve(puff, duration=30, *args, **kwargs):
    puff.anims.append(FlickerAnim(duration=duration, *args, **kwargs))

  def update(puff, *_):
    for anim in puff.anims:
      if anim.done:
        puff.anims.remove(anim)
        if type(anim) is FlickerAnim:
          puff.anims.clear()
      else:
        anim.update()
        if type(anim) is PoisonPuffVfx.FloatAnim:
          x, y = puff.offset
          PERIOD_X = 240 + puff.offset_period
          PERIOD_Y = 210 + puff.offset_period
          AMPLITUDE = 2 + puff.offset_amplitude
          xmod = anim.time // 3 * 3 % PERIOD_X / PERIOD_X
          ymod = anim.time // 3 * 3 % PERIOD_Y / PERIOD_Y
          if puff.offset_axis:
            xmod, ymod = ymod, xmod
          x += sin(xmod * puff.offset_direction * 2 * pi) * AMPLITUDE // 2 * 2
          y += sin(ymod * puff.offset_direction * 2 * pi) * AMPLITUDE // 2 * 2
          puff.pos = (x, y)
        elif type(anim) is OffsetMoveAnim:
          src_x, src_y = anim.src
          dest_x, dest_y = anim.dest
          offset_x, offset_y = anim.offset
          puff.pos = add_vector(puff.offset, (
            src_x - dest_x + offset_x,
            src_y - dest_y + offset_y
          ))
    if not puff.anims:
      puff.done = True

  def view(puff):
    flicker_anim = next((a for a in puff.anims if type(a) is FlickerAnim), None)
    if (puff.done
    or flicker_anim and not flicker_anim.visible
    or not flicker_anim and puff.flickering and puff.anims and puff.anims[0].time // 2 % 2):
      return []
    if puff.size == "tiny":
      puff_image = assets.sprites["fx_particle"][0]
      puff_image = replace_color(puff_image, BLACK, DARKBLUE)
    elif puff.size == "small":
      puff_image = assets.sprites["fx_smallspark"]
      puff_image = replace_color(puff_image, BLACK, VIOLET)
    elif puff.size == "medium":
      puff_image = assets.sprites["fx_poisonpuff_small"]
      puff_image = replace_color(puff_image, WHITE, DARKBLUE)
    elif puff.size == "large":
      puff_image = assets.sprites["fx_poisonpuff_large"]
      puff_image = replace_color(puff_image, WHITE, VIOLET)
    if type(puff.anim) is OffsetMoveAnim:
      puff_layer = "elems"
    else:
      puff_layer = "vfx"
    return [Sprite(
      image=puff_image,
      pos=puff.pos,
      layer=puff_layer,
    )]
