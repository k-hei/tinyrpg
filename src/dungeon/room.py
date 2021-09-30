from random import choice
from dungeon.features.room import Room
from lib.bounds import find_bounds
from lib.cell import neighborhood, manhattan, add as add_vector, subtract as subtract_vector
import debug

class Blob(Room):
  def find_border(cells):
    return list({n for c in cells for n in neighborhood(c) if n not in cells})

  def __init__(room, cells=None, origin=None, data=None, degree=0, *args, **kwargs):
    if type(data) is list:
      data = choice(data)
    if data:
      degree = data.degree
    if not cells:
      cells = data.extract_cells()
    rect = find_bounds(cells)
    room._cells = [subtract_vector(c, rect.topleft) for c in cells]
    room.origin = origin or rect.topleft
    room.data = data
    super().__init__(size=rect.size, cell=room.origin, degree=degree, *args, **kwargs)

  @property
  def origin(room):
    return room._origin

  @origin.setter
  def origin(room, origin):
    room._origin = origin
    room._outline = None
    room._visible_outline = None
    room._edges = None
    room._connectors = None
    room.connector_deltas = {}

  @property
  def cells(room):
    return [add_vector(c, room.origin) for c in room._cells]

  @property
  def border(room):
    return Blob.find_border(room.cells)

  @property
  def edges(room):
    if not room._edges:
      if room.data and callable(room.data.edges):
        room._edges = room.data.edges(room)
      elif room.data and room.data.edges:
        room._edges = [add_vector(e, room.origin) for e in room.data.edges]
      else:
        room_cells = room.cells
        room._edges = [e for e in room.border if len([n for n in neighborhood(e) if n in room_cells]) == 1 and room.find_connector(e)]
    return room._edges

  def find_connector(room, edge):
    room_cells = room.cells
    neighbor = next((n for n in neighborhood(edge) if n in room_cells), None)
    delta_x, delta_y = subtract_vector(edge, neighbor)
    connector = add_vector(edge, (delta_x * 2, delta_y * 2))
    if next((n for n in neighborhood(connector, diagonals=True) if n in room_cells), None):
      return None
    else:
      room.connector_deltas[connector] = (delta_x, delta_y)
      return connector

  @property
  def connectors(room):
    if not room._connectors:
      room._connectors = list({room.find_connector(e) for e in room.edges})
    return room._connectors

  @property
  def hitbox(room):
    return room.visible_outline

  @property
  def outline(room):
    if not room._outline:
      outline = []
      for cell in room.cells:
        outline += neighborhood(cell, diagonals=True)
      room._outline = set(outline) - set(room.cells)
    return room._outline

  @property
  def visible_outline(room):
    if not room._visible_outline:
      visible_outline = []
      for cell in room.cells:
        visible_outline += (
          neighborhood(cell, diagonals=True)
          + neighborhood(add_vector(cell, (0, -1)), diagonals=True)
        )
      room._visible_outline = set(visible_outline) - set(room.cells)
    return room._visible_outline

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

  def lock_special_doors(room, stage):
    if room.should_unlock(stage):
      return
    for door in room.get_doors(stage):
      if type(door).__name__ == "TreasureDoor":
        door.lock()

  def should_unlock(room, stage, actor=None):
    enemies = [e for e in room.get_enemies(stage) if e is not actor]
    pushtile = next((e for c in room.get_cells() for e in stage.get_elems_at(c) if type(e).__name__ == "PushTile"), None)
    return (
      not enemies
      and not pushtile
    )

  def resolve_hook(room, hook):
    return room.data and hook in room.data.hooks and room.data.hooks[hook]

  def trigger_hook(room, hook, *args, **kwargs):
    hook_id = hook
    if room.data and hook_id in room.data.hooks:
      hook = room.data.hooks[hook_id]
      not hook and debug.log(f"Failed to resolve \"{hook_id}\" hook \"{hook}\"")
      return hook and hook(room, *args, **kwargs)
    else:
      return False

  def on_place(room, stage):
    room.lock_special_doors(stage)
    return room.trigger_hook("on_place", stage)

  def on_focus(room, *args, **kwargs):
    if not super().on_focus(*args, **kwargs):
      return False
    return room.trigger_hook("on_focus", *args, **kwargs)

  def on_enter(room, *args, **kwargs):
    if not super().on_enter(*args, **kwargs):
      return False
    return room.trigger_hook("on_enter", *args, **kwargs)

  def on_walk(room, *args, **kwargs):
    return room.trigger_hook("on_walk", *args, **kwargs)

  def on_defeat(room, game, actor):
    if room.resolve_hook("on_defeat"):
      result = room.trigger_hook("on_defeat", game, actor)
      if result is not None: return result
    elif room.should_unlock(game.floor, actor):
      room.unlock(game)
      return True
    return super().on_defeat(game, actor)
