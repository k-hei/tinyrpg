from dataclasses import dataclass
from pygame import Surface

@dataclass
class Sprite:
  image: Surface = None
  pos: tuple[int, int] = (0, 0)
  offset: int = 0
  layer: str = None

  def copy(sprite):
    return Sprite(
      image=sprite.image,
      pos=sprite.pos,
      offset=sprite.offset,
      layer=sprite.layer
    )

  def draw(sprite, surface):
    surface.blit(sprite.image, sprite.pos)
