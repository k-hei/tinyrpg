from math import ceil
from pygame import Surface
import assets
from lib.sprite import Sprite
from anims.tween import TweenAnim
from lib.lerp import lerp
from easing.expo import ease_out

class EnterAnim(TweenAnim): pass
class ExitAnim(TweenAnim): pass

class Bg:
  PERIOD = 90

  def render(size):
    width, height = size
    tile_image = assets.sprites["bg_tile"]
    tile_width = tile_image.get_width()
    tile_height = tile_image.get_height()
    tile_surface = Surface((width + tile_width * 2, height + tile_height * 2))
    for row in range(ceil(tile_surface.get_height() / tile_height)):
      for col in range(ceil(tile_surface.get_width() / tile_width)):
        x = col * tile_width
        y = row * tile_height
        tile_surface.blit(tile_image, (x, y))
    return tile_surface

  def __init__(bg, size):
    bg.size = size
    bg.surface = None
    bg.exiting = False
    bg.time = 0
    bg.anims = []

  def init(bg):
    bg.surface = Bg.render(bg.size)

  def enter(bg):
    bg.exiting = False
    bg.anims.append(EnterAnim(easing=ease_out, duration=20))

  def exit(bg):
    bg.exiting = True
    bg.anims.append(ExitAnim(duration=10))

  def update(bg):
    if not bg.surface:
      bg.init()
    for anim in bg.anims:
      bg.anims.remove(anim) if anim.done else anim.update()
    bg.time += 1

  def draw(bg, surface):
    bg_sprite = bg.view()[0]
    surface.blit(bg_sprite.image, bg_sprite.pos)

  def view(bg):
    bg.update()
    tile_size = assets.sprites["bg_tile"].get_width()
    t = bg.time % bg.PERIOD / bg.PERIOD
    x = -t * tile_size
    bg_image = bg.surface
    bg_height = bg_image.get_height()
    bg_anim = next((a for a in bg.anims), None)
    if type(bg_anim) is EnterAnim:
      bg_height *= bg_anim.pos
    elif type(bg_anim) is ExitAnim:
      bg_height *= 1 - bg_anim.pos
    elif bg.exiting:
      return []
    return [Sprite(
      image=bg_image,
      pos=(x, x + bg.size[1] / 2),
      size=(bg_image.get_width(), bg_height),
      origin=Sprite.ORIGIN_LEFT,
    )]
