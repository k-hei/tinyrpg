from dungeon.features.room import Room
from dungeon.stage import Stage
from dungeon.props.door import Door
from random import choice
from lib.cell import add as add_cell

class SpecialRoom(Room):
  def __init__(feature, shape, elems=None, rooms=None, size=None, cell=None, *args, **kwargs):
    super().__init__(size=(size or shape and (len(shape[0]), len(shape)) or (0, 0)), cell=cell, *args, **kwargs)
    feature.shape = shape or []
    feature.elems = elems or []
    feature.rooms = rooms or {}

  def parse_char(char):
    if char == "#": return Stage.WALL
    if char == " ": return Stage.PIT
    if char == ",": return Stage.DOOR_WAY
    if char == ">": return Stage.STAIRS_DOWN
    if char == "<": return Stage.STAIRS_UP
    if char == "-": return Stage.STAIRS
    if char == "/": return Stage.STAIRS_RIGHT
    if char == "\\": return Stage.STAIRS_LEFT
    if char == "=": return Stage.LADDER
    if char == "O": return Stage.OASIS
    if char == "V": return Stage.OASIS_STAIRS
    if char == "·": return Stage.FLOOR_ELEV
    if char == "E": return Stage.EXIT
    return Stage.FLOOR

  def get_width(feature):
    return len(feature.shape[0]) if feature.shape else 0

  def get_height(feature):
    return len(feature.shape)

  def get_size(feature):
    return (feature.get_width(), feature.get_height())

  def place(feature, stage, cell=None, connectors=[]):
    if feature.placed:
      return False
    feature.placed = True
    feature.cell = cell or feature.cell
    x, y = feature.cell
    entrance = None
    for row in range(feature.get_height()):
      for col in range(feature.get_width()):
        cell = (col + x, row + y)
        char = feature.shape[row][col]
        tile = SpecialRoom.parse_char(char)
        stage.set_tile_at(cell, tile)
        try:
          actor_id = int(char)
          stage.spawn_elem_at(cell, feature.actors[actor_id])
        except ValueError:
          actor_id = None
        if tile is stage.STAIRS_DOWN:
          entrance = cell
        elif tile is stage.STAIRS_UP:
          stairs = cell
    for elem_cell, elem in feature.elems:
      elem_x, elem_y = elem_cell
      stage.spawn_elem_at((elem_x + x, elem_y + y), elem)
    stage.entrance = entrance or stage.entrance
    stage.rooms.append(feature)
    # stage.rooms += [Room(r.size, add_cell(r.cell, feature.cell)) for r in feature.rooms] or [feature]
    return True

  def create_floor(feature, use_edge=True, on_end=None):
    floor = Stage(size=(feature.get_width() + 2, feature.get_height() * 2))
    floor.fill(Stage.WALL)
    feature.place(floor, cell=(1, 1), connectors=[])
    edge = choice([(x, y) for (x, y) in feature.get_entrances() if y >= 0 and y <= feature.get_height() + 1])
    if feature.rooms:
      for x, y, width, height in feature.rooms:
        floor.rooms.append(Room((width, height), (x + 1, y + 1)))
      floor.entrance = edge
    else:
      edge_x, edge_y = edge
      floor.entrance = (edge_x, edge_y)
    if use_edge:
      door = feature.EntryDoor()
      door.open()
      floor.set_tile_at(floor.entrance, Stage.FLOOR)
      floor.spawn_elem_at(floor.entrance, door)
    else:
      floor.entrance = feature.get_center()
    floor.generator = type(feature).__name__
    yield floor

  def encode(room):
    return [room.cell, type(room).__name__]
