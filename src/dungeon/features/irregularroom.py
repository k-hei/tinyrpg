from math import ceil
from random import randint, choice
from pygame import Rect
from dungeon.features.specialroom import SpecialRoom
from lib.cell import neighborhood

class IrregularRoom(SpecialRoom):
  def __init__(room):
    room_size = randint(0, 3)
    room_width, room_height = (5 + room_size * 2, 4 + room_size * 3)
    super().__init__(size=(room_width, room_height))
    block_width = ceil(room_width / 2)
    block_height = ceil(room_height / 2)
    block_x = choice([0, room_width - block_width])
    block_y = choice([0, room_height - block_height])
    room.block = Rect(
      (block_x, block_y),
      (block_width, block_height)
    )

  def get_cells(room):
    cells = []
    col, row = room.cell or (0, 0)
    width, height = room.get_size()
    for y in range(height):
      for x in range(width):
        if not room.block.collidepoint((x, y)):
          cells.append((x + col, y + row))
    return cells

  def get_edges(room):
    room_edges = []
    room_cells = room.get_cells()
    room_x, room_y = room.cell
    block_corners = [
      (room.block.left + room_x, room.block.top + room_y),
      (room.block.right + room_x - 1, room.block.top + room_y),
      (room.block.left + room_x, room.block.bottom + room_y - 1),
      (room.block.right + room_x - 1, room.block.bottom + room_y - 1)
    ]
    for cell in room_cells:
      for neighbor in neighborhood(cell):
        if neighbor not in room_cells + room_edges + block_corners:
          room_edges.append(neighbor)
    return room_edges

  def get_border(room):
    edges = []
    cells = room.get_cells()
    for cell in cells:
      for x, y in neighborhood(cell, diagonals=True):
        if (x, y) not in cells + edges:
          edges.append((x, y))
        if (x, y - 1) not in cells + edges:
          edges.append((x, y - 1))
        if (x, y + 1) not in cells + edges:
          edges.append((x, y + 1))
    return edges
