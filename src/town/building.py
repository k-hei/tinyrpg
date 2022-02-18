from dataclasses import dataclass
from lib.vector import vector
from lib.sprite import Sprite
import assets
from config import TILE_SIZE

@dataclass
class TownBuilding:
  sprite_id: str
  pos: tuple[int, int]
  offset: tuple[int, int] = (0, 0)
  message: str = None # TODO: elem stub

  def update(building): # TODO: elem stub
    pass

  def view(building):
    return [Sprite(
      image=assets.sprites[building.sprite_id],
      pos=vector.add(building.pos, building.offset),
      layer="elems",
      offset=-TILE_SIZE, # prevent sorting actors behind door tile
      origin=Sprite.ORIGIN_BOTTOMLEFT,
    )]
