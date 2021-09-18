from dungeon.features.room import Room
from lib.bounds import find_bounds
from lib.cell import neighborhood, manhattan, add as add_vector, subtract as subtract_vector

class Blob(Room):
  def __init__(room, cells=None, origin=None, data=None, *args, **kwargs):
    if not cells:
      cells = data.extract_cells()
    rect = find_bounds(cells)
    room._cells = [subtract_vector(c, rect.topleft) for c in cells]
    room.origin = origin or rect.topleft
    room.data = data
    super().__init__(size=rect.size, cell=room.origin, *args, **kwargs)

  @property
  def cells(room):
    return [add_vector(c, room.origin) for c in room._cells]

  @property
  def border(room):
    room_cells = room.cells
    return list({n for c in room_cells for n in neighborhood(c) if n not in room_cells})

  @property
  def edges(room):
    room_cells = room.cells
    if room.data:
      return [add_vector(e, room.origin) for e, d in room.data.doors]
    else:
      return [e for e in room.border if len([n for n in neighborhood(e) if n in room_cells]) == 1 and room.find_connector(e)]

  def find_connector(room, edge):
    room_cells = room.cells
    neighbor = next((n for n in neighborhood(edge) if n in room_cells), None)
    delta_x, delta_y = subtract_vector(edge, neighbor)
    connector = add_vector(edge, (delta_x * 2, delta_y * 2))
    if next((n for n in neighborhood(connector, diagonals=True) if n in room_cells), None):
      return None
    else:
      return connector

  @property
  def connectors(room):
    return list({room.find_connector(e) for e in room.edges})

  @property
  def hitbox(room):
    hitbox = []
    for cell in room.cells:
      hitbox += neighborhood(cell, inclusive=True, radius=2)
    return set(hitbox)

  @property
  def outline(room):
    outline = []
    for cell in room.cells:
      outline += neighborhood(cell, diagonals=True)
    return set(outline) - set(room.cells)

  @property
  def visible_outline(room):
    visible_outline = []
    for cell in room.cells:
      neighbors = (
        neighborhood(cell, diagonals=True)
        + neighborhood(add_vector(cell, (0, -1)), diagonals=True)
      )
      visible_outline += neighbors
    return set(visible_outline) - set(room.cells)

  @property
  def rect(room):
    return find_bounds(room.cells)

  @property
  def cell(room):
    return room.origin

  @cell.setter
  def cell(room, cell):
    room.origin = cell

  def get_width(room):
    return room.rect.width

  def get_height(room):
    return room.rect.height

  def get_cells(room):
    return room.cells

  def get_edges(room):
    return room.edges

  def get_border(room):
    return list(room.outline)

  def get_center(room):
    return room.rect.center

  def get_outline(room):
    return list(room.visible_outline)

  def find_closest_cell(room, dest):
    return sorted(room.cells, key=lambda c: manhattan(c, dest))[0]
