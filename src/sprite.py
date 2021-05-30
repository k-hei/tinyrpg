from dataclasses import dataclass
from pygame import Surface
from pygame.transform import flip

@dataclass
class Sprite:
  image: Surface = None
  pos: tuple[int, int] = (0, 0)
  flip: tuple[bool, bool] = (False, False)
  origin: tuple[str, str] = ("top", "left")
  offset: int = 0
  layer: str = None

  def copy(sprite):
    return Sprite(
      image=sprite.image,
      pos=sprite.pos,
      flip=sprite.flip,
      offset=sprite.offset,
      layer=sprite.layer
    )

  def draw(sprite, surface):
    image = sprite.image
    flip_x, flip_y = sprite.flip
    if flip_x or flip_y:
      image = flip(image, flip_x, flip_y)
    x, y = sprite.pos
    origin_x, origin_y = sprite.origin
    if origin_x == "center":
      x -= image.get_width() // 2
    if origin_y == "center":
      y -= image.get_height() // 2
    if origin_y == "bottom":
      y -= image.get_height()
    surface.blit(image, (x, y))

  def depth(sprite, layers):
    _, y = sprite.pos
    try:
      depth = layers.index(sprite.layer)
    except ValueError:
      depth = 0
    return depth * 1000 + y + sprite.image.get_height() + sprite.offset
