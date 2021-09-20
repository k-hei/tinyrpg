from dungeon.features.room import Room
from lib.bounds import find_bounds
from lib.cell import neighborhood, manhattan, add as add_vector, subtract as subtract_vector
from resolve.hook import resolve_hook
import debug

class Blob(Room):
  def __init__(room, cells=None, origin=None, data=None, degree=0, *args, **kwargs):
    if not cells:
      cells = data.extract_cells()
    if data:
      degree = data.degree
    rect = find_bounds(cells)
    room._cells = [subtract_vector(c, rect.topleft) for c in cells]
    room.origin = origin or rect.topleft
    room.data = data
    super().__init__(size=rect.size, cell=room.origin, degree=degree, *args, **kwargs)

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
    if room.data and room.data.edges:
      return [add_vector(e, room.origin) for e in room.data.edges]
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
  def center(room):
    return room.rect.center

  @property
  def width(room):
    return room.data and room.data.size and room.data.size[0] or room.rect.width

  @property
  def height(room):
    return room.data and room.data.size and room.data.size[1] or room.rect.height

  @property
  def cell(room):
    return room.origin

  @cell.setter
  def cell(room, cell):
    room.origin = cell

  def get_width(room):
    return room.width

  def get_height(room):
    return room.height

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

  def get_tile_at(room, cell):
    if not room.data:
      return None
    x, y = cell
    return room.data.tiles[y * room.width + x]

  def on_place(room, stage):
    if room.data and "on_place" in room.data.hooks:
      on_place = resolve_hook(room.data.hooks["on_place"])
      not on_place and debug.log("Failed to resolve \"on_place\" hook \"{}\"".format(room.data.hooks["on_place"]))
      return on_place and on_place(room, stage)

  def on_focus(room, *args, **kwargs):
    if not super().on_focus(*args, **kwargs):
      return False
    if room.data and "on_focus" in room.data.hooks:
      on_focus = resolve_hook(room.data.hooks["on_focus"])
      not on_focus and debug.log("Failed to resolve \"on_focus\" hook \"{}\"".format(room.data.hooks["on_focus"]))
      return on_focus and on_focus(room, *args, **kwargs)
    else:
      return False

  def on_enter(room, *args, **kwargs):
    if not super().on_enter(*args, **kwargs):
      return False
    if room.data and "on_enter" in room.data.hooks:
      on_enter = resolve_hook(room.data.hooks["on_enter"])
      not on_enter and debug.log("Failed to resolve \"on_enter\" hook \"{}\"".format(room.data.hooks["on_enter"]))
      return on_enter and on_enter(room, *args, **kwargs)
    else:
      return False

  def on_defeat(room, *args, **kwargs):
    if room.data and "on_defeat" in room.data.hooks:
      on_defeat = resolve_hook(room.data.hooks["on_defeat"])
      not on_defeat and debug.log("Failed to resolve \"on_defeat\" hook \"{}\"".format(room.data.hooks["on_defeat"]))
      return on_defeat and on_defeat(room, *args, **kwargs)
    else:
      return super().on_defeat(*args, **kwargs)
