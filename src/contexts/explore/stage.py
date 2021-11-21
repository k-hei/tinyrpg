from config import TILE_SIZE

class Stage:
  def __init__(stage, tiles, elems=None, links=None, tile_size=TILE_SIZE, bg=None):
    stage.tiles = tiles
    stage.elems = elems or []
    stage.links = links or []
    stage.rooms = []
    stage.tile_size = tile_size
    stage.bg = bg

  def get_tile_at(stage, cell):
    return stage.tiles.get(*cell)

  def set_tile_at(stage, cell, tile):
    return stage.tiles.set(*cell, tile)

  def get_elem_at(stage, cell):
    return None

  def get_elems_at(stage, cell):
    return []

  def spawn_elem_at(stage, cell, elem):
    elem.spawn(stage, cell)
    if elem not in stage.elems:
      stage.elems.append(elem)
    return elem
