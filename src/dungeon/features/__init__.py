from dungeon.stage import Stage
from dungeon.room import Room

class Feature:
  def __init__(feature):
    feature.actors = []
    feature.shape = []
    feature.rooms = []
    feature.cell = None

  def get_width(feature):
    return len(feature.shape[0]) if feature.shape else 0

  def get_height(feature):
    return len(feature.shape)

  def get_size(feature):
    return (feature.get_width(), feature.get_height())

  def get_cells(feature):
    x, y = feature.cell or (0, 0)
    cells = []
    width = feature.get_width()
    height = feature.get_height()
    for row in range(height):
      for col in range(width):
        cells.append((col + x, row + y))
    return cells

  def get_edges(feature):
    return []

  def place(feature, stage, cell):
    feature.cell = cell
    x, y = cell
    entrance, stairs = None, None
    cells = feature.get_cells()
    for row in range(feature.get_height()):
      for col in range(feature.get_width()):
        cell = (col + x, row + y)
        char = feature.shape[row][col]
        tile = parse_char(char)
        stage.set_tile_at(cell, tile)
        try:
          actor_id = int(char)
          stage.spawn_elem(feature.actors[actor_id], cell)
        except ValueError:
          actor_id = None
        if tile is Stage.STAIRS_DOWN:
          entrance = cell
        elif tile is Stage.STAIRS_UP:
          stairs = cell
    stage.entrance = entrance or stage.entrance
    stage.stairs = stairs or stage.stairs
    for col, row, cols, rows in feature.rooms:
      stage.rooms.append(Room((cols, rows), (col + x, row + y)))

def parse_char(char):
  if char == "#": return Stage.WALL
  if char == " ": return Stage.PIT
  if char == "+": return Stage.DOOR
  if char == "-": return Stage.DOOR_LOCKED
  if char == "*": return Stage.DOOR_HIDDEN
  if char == "!": return Stage.MONSTER_DEN
  if char == ">": return Stage.STAIRS_DOWN
  if char == "<": return Stage.STAIRS_UP
  return Stage.FLOOR
