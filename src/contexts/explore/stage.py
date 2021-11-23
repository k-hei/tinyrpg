from config import TILE_SIZE

class Stage:
  def __init__(stage, tiles, elems=None, rooms=None, links=None, tile_size=TILE_SIZE, bg=None):
    stage.tiles = tiles
    stage.elems = elems or []
    stage.links = links or []
    stage.rooms = rooms or []
    stage.tile_size = tile_size
    stage.bg = bg

  def contains(stage, cell):
    return stage.tiles.contains(*cell)

  def get_tile_at(stage, cell):
    return stage.tiles.get(*cell)

  def set_tile_at(stage, cell, tile):
    return stage.tiles.set(*cell, tile)

  def get_elem_at(stage, cell):
    return None

  def get_elems_at(stage, cell):
    return [e for e in stage.elems if e.cell == cell]

  def spawn_elem_at(stage, cell, elem):
    elem.spawn(stage, cell)
    if elem not in stage.elems:
      stage.elems.append(elem)
    return elem

  def is_cell_opaque(stage, cell):
    tile = stage.get_tile_at(cell)
    return not tile or tile.opaque
