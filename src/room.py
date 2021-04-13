class Room:
  def __init__(room, size, cell=None):
    room.size = size
    room.cell = cell

  def get_width(room):
    room_width, _ = room.size
    return room_width

  def get_height(room):
    _, room_height = room.size
    return room_height

  def get_cells(room):
    cells = []
    (room_width, room_height) = room.size
    (room_x, room_y) = room.cell
    for y in range(room_height):
      for x in range(room_width):
        cells.append((x + room_x, y + room_y))
    return cells

  def get_center(room):
    (room_width, room_height) = room.size
    (room_x, room_y) = room.cell
    return (room_x + room_width // 2, room_y + room_height // 2)

  def get_edges(room):
    (room_width, room_height) = room.size
    (left, top) = room.cell
    right = left + room_width
    bottom = top + room_height

    edges = []
    for x in range(left, right):
      edges.append((x, top - 1))
      edges.append((x, bottom))

    for y in range(top, bottom):
      edges.append((left - 1, y))
      edges.append((right, y))

    return edges

  def get_border(room):
    (room_width, room_height) = room.size
    (left, top) = room.cell
    right = left + room_width
    bottom = top + room_height

    edges = []
    for x in range(left - 1, right + 1):
      edges.append((x, top - 1))
      edges.append((x, bottom))

    for y in range(top, bottom):
      edges.append((left - 1, y))
      edges.append((right, y))

    return edges
