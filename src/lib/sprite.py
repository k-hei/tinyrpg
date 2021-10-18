from dataclasses import dataclass
from pygame import Rect, Surface, SRCALPHA
from pygame.transform import flip, scale
import lib.vector as vector

@dataclass
class Sprite:
  ORIGIN_CENTER = ("center", "center")
  ORIGIN_LEFT = ("left", "center")
  ORIGIN_RIGHT = ("right", "center")
  ORIGIN_TOP = ("center", "top")
  ORIGIN_BOTTOM = ("center", "bottom")
  ORIGIN_TOPLEFT = ("left", "top")
  ORIGIN_TOPRIGHT = ("right", "top")
  ORIGIN_BOTTOMLEFT = ("left", "bottom")
  ORIGIN_BOTTOMRIGHT = ("right", "bottom")

  image: Surface = None
  pos: tuple[int, int] = (0, 0)
  size: tuple[int, int] = None
  flip: tuple[bool, bool] = (False, False)
  origin: tuple[str, str] = None
  offset: int = 0
  layer: str = None
  target: any = None
  key: str = None

  @property
  def rect(sprite):
    size = sprite.size or sprite.image.get_size()
    return Rect(*sprite.pos, *size)

  def copy(sprite):
    return Sprite(
      key=sprite.key,
      image=sprite.image,
      pos=sprite.pos,
      size=sprite.size,
      flip=sprite.flip,
      origin=sprite.origin,
      offset=sprite.offset,
      layer=sprite.layer,
      target=sprite.target
    )

  def move(sprite, offset):
    sprite.pos = vector.add(sprite.pos, offset)

  def move_all(sprites, offset):
    for sprite in sprites:
      sprite.move(offset)
    return sprites

  def draw(sprite, surface, offset=(0, 0), origin=None):
    image = sprite.image
    flip_x, flip_y = sprite.flip
    if flip_x or flip_y:
      image = flip(image, flip_x, flip_y)
    width, height = sprite.size or (None, None)
    if sprite.size and (width != image.get_width() or height != image.get_height()):
      scaled_image = scale(image, (int(width), int(height)))
    else:
      scaled_image = image
    if scaled_image is None:
      return

    x, y = sprite.pos

    origin_x, origin_y = sprite.origin or ("top", "left")
    if origin_x == "center":
      x -= scaled_image.get_width() // 2
    if origin_x == "right":
      x -= scaled_image.get_width()
    if origin_y == "center":
      y -= scaled_image.get_height() // 2
    if origin_y == "bottom":
      y -= scaled_image.get_height()

    if origin:
      origin_x, origin_y = origin
      if origin_x == "left":
        x += image.get_width() // 2
      if origin_x == "right":
        x -= image.get_width() // 2
      if origin_y == "top":
        y += image.get_height() // 2
      elif origin_y == "bottom":
        y -= image.get_height() // 2

    offset_x, offset_y = offset
    surface.blit(scaled_image, (x + offset_x, y + offset_y))

  def depth(sprite, layers):
    _, y = sprite.pos
    try:
      depth = layers.index(sprite.layer)
    except ValueError:
      depth = 0
    return depth * 1000 + y + sprite.offset


class SpriteMask(Sprite):
  def __init__(mask, size, children, pos=(0, 0)):
    super().__init__(size=size, pos=pos)
    mask.image = None
    mask.children = children

  def move(mask, offset):
    Sprite.move(mask, offset)

  def render(mask):
    if not mask.image:
      mask.image = Surface(mask.size, flags=SRCALPHA)
    mask.image.fill((0, 0, 0, 0))
    for sprite in mask.children:
      sprite.draw(mask.image)

  def draw(mask, surface):
    mask.render()
    surface.blit(mask.image, mask.pos)
