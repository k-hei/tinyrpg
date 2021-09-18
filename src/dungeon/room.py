from dungeon.features.room import Room
from lib.bounds import find_bounds
from lib.cell import neighborhood, manhattan, add as add_vector, subtract as subtract_vector

class Blob(Room):
  def __init__(blob, cells=None, origin=None, data=None):
    if not cells:
      cells = data.extract_cells()
    rect = find_bounds(cells)
    blob._cells = [subtract_vector(c, rect.topleft) for c in cells]
    blob.origin = origin or rect.topleft
    blob.data = data
    super().__init__(size=rect.size, cell=blob.origin)

  @property
  def cells(blob):
    return [add_vector(c, blob.origin) for c in blob._cells]

  @property
  def border(blob):
    blob_cells = blob.cells
    return list({n for c in blob_cells for n in neighborhood(c) if n not in blob_cells})

  @property
  def edges(blob):
    blob_cells = blob.cells
    return [e for e in blob.border if len([n for n in neighborhood(e) if n in blob_cells]) == 1 and blob.find_connector(e)]

  def find_connector(blob, edge):
    blob_cells = blob.cells
    neighbor = next((n for n in neighborhood(edge) if n in blob_cells), None)
    delta_x, delta_y = subtract_vector(edge, neighbor)
    connector = add_vector(edge, (delta_x * 2, delta_y * 2))
    if next((n for n in neighborhood(connector, diagonals=True) if n in blob_cells), None):
      return None
    else:
      return connector

  @property
  def connectors(blob):
    return list({blob.find_connector(e) for e in blob.edges})

  @property
  def hitbox(blob):
    hitbox = []
    for cell in blob.cells:
      hitbox += neighborhood(cell, inclusive=True, radius=2)
    return set(hitbox)

  @property
  def outline(blob):
    outline = []
    for cell in blob.cells:
      outline += neighborhood(cell, diagonals=True)
    return set(outline) - set(blob.cells)

  @property
  def visible_outline(blob):
    visible_outline = []
    for cell in blob.cells:
      neighbors = (
        neighborhood(cell, diagonals=True)
        + neighborhood(add_vector(cell, (0, -1)), diagonals=True)
      )
      visible_outline += neighbors
    return set(visible_outline) - set(blob.cells)

  @property
  def rect(blob):
    return find_bounds(blob.cells)

  @property
  def cell(blob):
    return blob.origin

  @cell.setter
  def cell(blob, cell):
    blob.origin = cell

  def get_width(blob):
    return blob.rect.width

  def get_height(blob):
    return blob.rect.height

  def get_cells(blob):
    return blob.cells

  def get_edges(blob):
    return blob.edges

  def get_border(blob):
    return list(blob.outline)

  def get_center(blob):
    return blob.rect.center

  def get_outline(blob):
    return list(blob.visible_outline)

  def find_closest_cell(blob, dest):
    return sorted(blob.cells, key=lambda c: manhattan(c, dest))[0]
