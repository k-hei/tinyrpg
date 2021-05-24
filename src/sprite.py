from dataclasses import dataclass
from pygame import Surface
from pygame.transform import flip

@dataclass
class Sprite:
  image: Surface = None
  pos: tuple[int, int] = (0, 0)
  flip: tuple[bool, bool] = (False, False)
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
    surface.blit(image, sprite.pos)
