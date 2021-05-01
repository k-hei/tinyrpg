from dungeon.features.room import Room

class SpecialRoom(Room):
  def __init__(room, degree=0, secret=False):
    super().__init__(room.get_size(), degree, secret)

  def get_width(room):
    return len(room.shape[0]) if room.shape else 0

  def get_height(room):
    return len(room.shape)

  def get_size(room):
    return (room.get_width(), room.get_height())

  def place(room, stage):
    def parse_char(char):
      if char == "#": return stage.WALL
      if char == " ": return stage.PIT
      if char == "+": return stage.DOOR
      if char == "-": return stage.DOOR_LOCKED
      if char == "*": return stage.DOOR_HIDDEN
      if char == ">": return stage.STAIRS_DOWN
      if char == "<": return stage.STAIRS_UP
      if char == "=": return stage.COFFIN
      if char == "O": return stage.OASIS
      return stage.FLOOR

    x, y = room.cell or (0, 0)
    entrance, stairs = None, None
    for row in range(room.get_height()):
      for col in range(room.get_width()):
        cell = (col + x, row + y)
        char = room.shape[row][col]
        tile = parse_char(char)
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
