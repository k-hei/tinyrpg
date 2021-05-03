from dataclasses import dataclass
from pygame import Surface

@dataclass
class Sprite:
  image: Surface
  pos: tuple[int, int]
  offset: int = 0
  layer: str = None
  tile: bool = False

  def copy(sprite):
    return Sprite(
      image=sprite.image,
      pos=sprite.pos,
      offset=sprite.offset,
      layer=sprite.layer,
      tile=sprite.tile
    )

  def draw(sprite, surface):
    surface.blit(sprite.image, sprite.pos)
