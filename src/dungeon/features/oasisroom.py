from dungeon.features.specialroom import SpecialRoom
from dungeon.stage import Stage
from assets import load as use_assets
from sprite import Sprite
from config import TILE_SIZE
from random import choice

class OasisRoom(SpecialRoom):
  def __init__(room, secret=False):
    room.shape = [
      "#...#",
      ".....",
      ".OOO.",
      ".OOO.",
      ".OOO.",
      ".....",
      "#...#"
    ]
    super().__init__(degree=1, secret=secret)

  def get_cells(room):
    return [c for c in super().get_cells() if c not in room.get_corners()]

  def get_border(room):
    return super().get_border() + room.get_corners()

  def get_edges(room):
    x, y = room.cell or (0, 0)
    width, height = room.size
    return [
      (x + width // 2, y - 1),
      (x + width // 2, y + height + 1),
      (x - 1, y + height // 2),
      (x + width, y + height // 2),
    ]

  def place(room, stage):
    sprites = use_assets().sprites
    super().place(stage)
    x, y = room.cell or (0, 0)
    cells = []
    for row in range(room.get_height()):
      for col in range(room.get_width()):
        cell = (col + x, row + y)
        char = room.shape[row][col]
        if SpecialRoom.parse_char(char) is Stage.FLOOR:
          cells.append(cell)

    for i in range(3):
      cell = choice(cells)
      cells.remove(cell)
      x, y = cell
      image = sprites["oasis_palm"]
      sprite_x = x * TILE_SIZE
      sprite_y = (y + 1) * TILE_SIZE - image.get_height()
      stage.decors.append(Sprite(
        image=image,
        pos=(sprite_x, sprite_y),
        offset=-1,
        layer="elems"
      ))

    for i in range(8):
      cell = choice(cells)
      cells.remove(cell)
      x, y = cell
      image = sprites["oasis_grass"]
      sprite_x = x * TILE_SIZE
      sprite_y = y * TILE_SIZE
      stage.decors.append(Sprite(
        image=image,
        pos=(sprite_x, sprite_y),
        offset=-1,
        layer="tiles"
      ))
