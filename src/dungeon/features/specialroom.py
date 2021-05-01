from dungeon.features.room import Room
from dungeon.stage import Stage

class SpecialRoom(Room):
  def __init__(room, degree=0, secret=False):
    super().__init__(room.get_size(), degree, secret)

  def parse_char(char):
    if char == "#": return Stage.WALL
    if char == " ": return Stage.PIT
    if char == "+": return Stage.DOOR
    if char == "-": return Stage.DOOR_LOCKED
    if char == "*": return Stage.DOOR_HIDDEN
    if char == ">": return Stage.STAIRS_DOWN
    if char == "<": return Stage.STAIRS_UP
    if char == "=": return Stage.COFFIN
    if char == "O": return Stage.OASIS
    if char == "V": return Stage.OASIS
    return Stage.FLOOR

  def get_width(room):
    return len(room.shape[0]) if room.shape else 0

  def get_height(room):
    return len(room.shape)

  def get_size(room):
    return (room.get_width(), room.get_height())

  def place(room, stage):
    x, y = room.cell or (0, 0)
    entrance, stairs = None, None
    for row in range(room.get_height()):
      for col in range(room.get_width()):
        cell = (col + x, row + y)
        char = room.shape[row][col]
        tile = SpecialRoom.parse_char(char)
        stage.set_tile_at(cell, tile)
        try:
          actor_id = int(char)
          stage.spawn_elem(room.actors[actor_id], cell)
        except ValueError:
          actor_id = None
        if tile is stage.STAIRS_DOWN:
          entrance = cell
        elif tile is stage.STAIRS_UP:
          stairs = cell
    stage.entrance = entrance or stage.entrance
    stage.stairs = stairs or stage.stairs
