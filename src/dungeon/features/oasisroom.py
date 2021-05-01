from dungeon.features.specialroom import SpecialRoom
from dungeon.stage import Stage
from assets import load as use_assets
from sprite import Sprite
from config import TILE_SIZE
from random import randint, choice

class OasisRoom(SpecialRoom):
  def __init__(room, secret=False):
    room.shape = [
      "#...#",
      ".....",
      ".OVO.",
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
    floor_cells = []
    for row in range(room.get_height()):
      for col in range(room.get_width()):
        cell = (col + x, row + y)
        char = room.shape[row][col]
        if SpecialRoom.parse_char(char) is stage.FLOOR:
          floor_cells.append(cell)

    for i in range(3):
      cell = choice(floor_cells)
      floor_cells.remove(cell)
      x, y = cell
      image = sprites["oasis_palm"]
      sprite_x = x * TILE_SIZE
      sprite_y = (y + 1) * TILE_SIZE - image.get_height()
      stage.decors.append(Sprite(
        image=image,
        pos=(sprite_x, sprite_y),
        offset=-1,
        layer="elems",
        tile=True
      ))

    for i in range(8):
      cell = choice(floor_cells)
      floor_cells.remove(cell)
      x, y = cell
      image = sprites["oasis_grass"]
      for j in range(2):
        for k in range(2):
          if randint(1, 5) == 1:
            sprite_x = x * TILE_SIZE + j * 16
            sprite_y = y * TILE_SIZE + k * 16
            stage.decors.append(Sprite(
              image=image,
              pos=(sprite_x, sprite_y),
              offset=-1,
              tile=True
            ))

    x, y = room.cell or (0, 0)
    oasis_cells = []
    for row in range(room.get_height()):
      for col in range(room.get_width()):
        cell = (col + x, row + y)
        char = room.shape[row][col]
        if SpecialRoom.parse_char(char) is stage.OASIS:
          oasis_cells.append(cell)

    for i in range(3):
      cell = choice(oasis_cells)
      oasis_cells.remove(cell)
      x, y = cell
      image = sprites["oasis_wave"]
      corners = []
      if (stage.get_tile_at((x - 1, y)) is stage.OASIS
      and stage.get_tile_at((x, y - 1)) is stage.OASIS):
        corners.append((0, 0))
      if (stage.get_tile_at((x + 1, y)) is stage.OASIS
      and stage.get_tile_at((x, y - 1)) is stage.OASIS):
        corners.append((1, 0))
      if (stage.get_tile_at((x - 1, y)) is stage.OASIS
      and stage.get_tile_at((x, y + 1)) is stage.OASIS):
        corners.append((0, 1))
      if (stage.get_tile_at((x + 1, y)) is stage.OASIS
      and stage.get_tile_at((x, y + 1)) is stage.OASIS):
        corners.append((1, 1))
      if corners:
        corner_x, corner_y = choice(corners)
        sprite_x = x * TILE_SIZE + corner_x * 16
        sprite_y = y * TILE_SIZE + corner_y * 16
        stage.decors.append(Sprite(
          image=image,
          pos=(sprite_x, sprite_y)
        ))
