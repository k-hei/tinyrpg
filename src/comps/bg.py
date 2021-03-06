from math import ceil
from pygame import Surface, SRCALPHA
import assets
from lib.sprite import Sprite, SpriteMask
from anims.tween import TweenAnim
from lib.lerp import lerp
from easing.expo import ease_out
from config import WINDOW_SIZE

class EnterAnim(TweenAnim): pass
class ExitAnim(TweenAnim): pass

class Bg:
  def render(size, sprite_id="bgtile"):
    width, height = size
    tile_image = assets.sprites[sprite_id]
    tile_width = tile_image.get_width()
    tile_height = tile_image.get_height()
    tile_surface = Surface((width + tile_width * 2, height + tile_height * 2), flags=SRCALPHA)
    for row in range(ceil(tile_surface.get_height() / tile_height)):
      for col in range(ceil(tile_surface.get_width() / tile_width)):
        x = col * tile_width
        y = row * tile_height
        tile_surface.blit(tile_image, (x, y))
    return tile_surface

  def __init__(bg, size=WINDOW_SIZE, sprite_id="bgtile", period=0):
    bg.size = size
    bg.sprite_id = sprite_id
    bg.period = period or assets.sprites[sprite_id].get_width() * 3
    bg.surface = None
    bg.exiting = False
    bg.time = 0
    bg.anims = []

  @property
  def width(bg):
    return bg.size[0]

  @property
  def height(bg):
    return bg.size[1]

  def init(bg):
    bg.surface = Bg.render(bg.size, bg.sprite_id)

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
    surface.blit(bg_sprite.image, (
      bg_sprite.pos[0],
      bg_sprite.pos[1] - bg.size[1] / 2
    ))

  def view(bg):
    bg.update()
    tile_size = assets.sprites[bg.sprite_id].get_width()
    t = bg.time % bg.period / bg.period
    x = -t * tile_size

    bg_image = bg.surface
    bg_height = bg_image.get_height()
    bg_anim = bg.anims and next((a for a in bg.anims), None)
    if type(bg_anim) is EnterAnim:
      bg_height *= bg_anim.pos
    elif type(bg_anim) is ExitAnim:
      bg_height *= 1 - bg_anim.pos
    elif bg.exiting:
      return []

    bg_sprite = Sprite(
      image=bg_image,
      pos=(x, x + bg.size[1] / 2),
      size=(bg_image.get_width(), bg_height),
      origin=Sprite.ORIGIN_LEFT
    )

    return [bg_sprite] if bg.size == WINDOW_SIZE else [SpriteMask(
      size=bg.size,
      children=[bg_sprite],
    )]
