from dungeon.features import Feature
from lib.cell import is_adjacent, neighbors

class Maze(Feature):
  def __init__(maze, cells):
    super().__init__()
    maze.cells = cells

  def get_cells(maze):
    return maze.cells

  def get_edges(maze):
    edges = []
    for cell in maze.cells:
      x, y = cell
      for neighbor in neighbors(cell):
        if not neighbor in edges + maze.cells:
          edges.append(neighbor)
    return edges

  def get_ends(maze):
    return [c for c in maze.cells if len([o for o in maze.cells if is_adjacent(o, c)]) <= 1]
