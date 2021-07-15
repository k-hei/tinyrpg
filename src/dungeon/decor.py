from dataclasses import dataclass
from colors.palette import WHITE
from sprite import Sprite
from assets import load as use_assets
from config import TILE_SIZE
from filters import replace_color

@dataclass
class Decor:
  kind: str
  cell: tuple[int, int]
  offset: tuple[int, int] = (0, 0)
  color: tuple[int, int, int] = WHITE

  def view(decor):
    col, row = decor.cell
    offset_x, offset_y = decor.offset
    image = use_assets().sprites[decor.kind]
    if decor.color != WHITE:
      image = replace_color(image, WHITE, decor.color)
    x = col * TILE_SIZE + offset_x
    y = row * TILE_SIZE + offset_y
    return [Sprite(
      image=image,
      pos=(x, y),
      layer="decors"
    )]
