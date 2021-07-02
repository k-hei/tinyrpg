from dungeon.features.room import Room
from dungeon.stage import Stage
from dungeon.props.door import Door
from random import choice

class SpecialRoom(Room):
  def __init__(feature, shape, elems=None, rooms=None, *args, **kwargs):
    feature.shape = shape or []
    feature.elems = elems or {}
    feature.rooms = rooms or {}
    super().__init__(shape and (len(shape[0]), len(shape)) or (0, 0), *args, **kwargs)

  def parse_char(char):
    if char == "#": return Stage.WALL
    if char == " ": return Stage.PIT
    if char == "+": return Stage.DOOR
    if char == "*": return Stage.DOOR_HIDDEN
    if char == ">": return Stage.STAIRS_DOWN
    if char == "<": return Stage.STAIRS_UP
    if char == "-": return Stage.STAIRS
    if char == "=": return Stage.LADDER
    if char == "O": return Stage.OASIS
    if char == "V": return Stage.OASIS_STAIRS
    if char == "·": return Stage.FLOOR_ELEV
    return Stage.FLOOR

  def get_width(feature):
    return len(feature.shape[0]) if feature.shape else 0

  def get_height(feature):
    return len(feature.shape)

  def get_size(feature):
    return (feature.get_width(), feature.get_height())

  def effect(feature, game):
    pass

  def place(feature, stage, cell=None):
    feature.cell = cell or feature.cell or (0, 0)
    x, y = feature.cell
    entrance, stairs = None, None
    for row in range(feature.get_height()):
      for col in range(feature.get_width()):
        cell = (col + x, row + y)
        char = feature.shape[row][col]
        tile = SpecialRoom.parse_char(char)
        if (tile is stage.FLOOR_ELEV
        and SpecialRoom.parse_char(feature.shape[row + 1][col]) is stage.FLOOR):
          tile = stage.WALL_ELEV
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
    stage.entrance = entrance or stage.entrance
    stage.stairs = stairs or stage.stairs

  def create_floor(feature):
    floor = Stage(size=(feature.get_width() + 2, feature.get_height() * 2))
    floor.fill(Stage.WALL)
    feature.place(floor, cell=(1, 1))
    edge = choice([(x, y) for (x, y) in feature.get_edges() if y >= 0 and y <= feature.get_height() + 1])
    if feature.rooms:
      for x, y, width, height in feature.rooms:
        floor.rooms.append(Room((width, height), (x + 1, y + 1)))
      floor.entrance = edge
    else:
      floor.rooms.append(Room(feature.get_size(), (1, 1)))
      edge_x, edge_y = edge
      floor.entrance = (edge_x, edge_y)
    door = Door()
    door.open()
    floor.set_tile_at(floor.entrance, Stage.FLOOR)
    floor.spawn_elem_at(floor.entrance, door)
    return floor
