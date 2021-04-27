from cell import is_adjacent

class Maze:
  def __init__(maze, cells):
    maze.cells = cells

  def get_cells(maze):
    return maze.cells

  def get_edges(maze):
    edges = []
    for cell in maze.cells:
      x, y = cell
      adj_cells = [
        (x - 1, y),
        (x, y - 1),
        (x + 1, y),
        (x, y + 1)
      ]
      for adj in adj_cells:
        if not adj in edges + maze.cells:
          edges.append(adj)
    return edges

  def get_ends(maze):
    return [c for c in maze.cells if len([o for o in maze.cells if is_adjacent(o, c)]) <= 1]
