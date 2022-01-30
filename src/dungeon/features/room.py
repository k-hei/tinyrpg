from random import choice
from math import ceil
from dungeon.features import Feature
from dungeon.actors import DungeonActor
from dungeon.props.door import Door
import locations.default.tileset as tileset
from config import ROOM_WIDTHS, ROOM_HEIGHTS

class Room(Feature):
  EntryDoor = Door
  ExitDoor = Door

  def __init__(room, size=None, cell=None, entered=False, focused=False, *args, **kwargs):
    super().__init__(*args, **kwargs)
    room.size = size or (choice(ROOM_WIDTHS), choice(ROOM_HEIGHTS))
    room.cell = cell
    room.entered = entered
    room.focused = focused

  def get_width(room):
    width, _ = room.get_size()
    return width

  def get_height(room):
    _, height = room.get_size()
    return height

  def get_area(room):
    return room.get_width() * room.get_height()

  def get_size(room):
    return room.size

  def get_center(room):
    width, height = room.get_size()
    x, y = room.cell or (0, 0)
    return (
      x + ceil(width / 2) - 1,
      y + ceil(height / 2) - 1
    )

  def get_cells(room):
    cells = []
    col, row = room.cell or (0, 0)
    width, height = room.get_size()
    for y in range(height):
      for x in range(width):
        cells.append((x + col, y + row))
    return cells

  def get_edges(room):
    room_width, room_height = room.size
    left, top = room.cell
    right = left + room_width
    bottom = top + room_height
    edges = []
    for x in range(left, right):
      edges.append((x, top - 2))
      edges.append((x, top - 1))
      edges.append((x, bottom))
      edges.append((x, bottom + 1))
    for y in range(top, bottom):
      edges.append((left - 1, y))
      edges.append((right, y))
    return edges

  def get_corners(room):
    x, y = room.cell or (0, 0)
    width, height = room.size
    return [
      (x, y),
      (x + width - 1, y),
      (x, y + height - 1),
      (x + width - 1, y + height - 1),
    ]

  def get_outline(room):
    left, top = room.cell
    right = left + room.get_width()
    bottom = top + room.get_height()

    edges = []
    for x in range(left - 1, right + 1):
      edges.append((x, top - 1))
      edges.append((x, bottom))

    for y in range(top, bottom):
      edges.append((left - 1, y))
      edges.append((right, y))

    return edges

  def get_border(room):
    left, top = room.cell
    right = left + room.get_width()
    bottom = top + room.get_height()

    edges = []
    for x in range(left - 1, right + 1):
      edges.append((x, top - 2))
      edges.append((x, top - 1))
      edges.append((x, bottom))
      edges.append((x, bottom + 1))

    for y in range(top, bottom):
      edges.append((left - 1, y))
      edges.append((right, y))

    return edges

  def get_doors(room, stage):
    return [e for c in room.get_border() for e in stage.get_elems_at(c) if isinstance(e, Door)]

  def get_doorways(room, stage):
    return [e for e in room.get_edges() if not issubclass(stage.get_tile_at(e), tileset.Wall)]

  def get_enemies(room, stage):
    return [e for c in room.get_cells() for e in stage.get_elems_at(c) if (
      e and isinstance(e, DungeonActor) and e.faction == "enemy"
    )]

  def get_slots(room, cell=None):
    room_x, room_y = cell or room.cell or (0, 0)
    slots = []
    for y in range(room.get_height()):
      for x in range(room.get_width()):
        col, row = x + room_x, y + room_y
        if col % 2 == 1 and row % 3 == 1:
          slots.append((col, row))
    return slots

  def lock(room, game):
    for door in room.get_doors(game.stage):
      door.handle_close(game)

  def unlock(room, game, open=False):
    for door in room.get_doors(game.stage):
      if door.locked:
        if open:
          door.handle_open(game)
        else:
          door.unlock()

  def on_focus(room, game):
    if room.focused:
      return False
    room.focused = True
    for door in room.get_doors(game.stage):
      door.focus = game.hero.cell
      # door.align(game)
    return True

  def on_blur(room, game):
    for door in room.get_doors(game.stage):
      door.focus = game.hero.cell
      # door.align(game)

  def on_enter(room, game):
    if room.entered:
      return False
    room.entered = True
    return True

  def on_exit(room, game): pass

  def on_defeat(room, game, target):
    return True

  def validate(room, cell, slots):
    for slot in room.get_slots(cell):
      if slot not in slots:
        return False
    return True

  def filter_slots(room, slots):
    return [s for s in slots if room.validate(s, slots)]

  def place(room, stage, *args, **kwargs):
    if not super().place(stage, *args, **kwargs):
      return False
    stage.rooms.append(room)
    return True

  def encode(room):
    x, y = room.cell
    width, height = room.size
    props = {
      **(room.entered and { "entered": room.entered } or {}),
      **(room.focused and { "focused": room.focused } or {}),
    }
    return [[x, y, width, height], type(room).__name__, *(props and [props] or [])]
