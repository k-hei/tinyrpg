from dungeon.features.specialroom import SpecialRoom
from dungeon.stage import Stage
from dungeon.decor import Decor
from dungeon.props.palm import Palm
from dungeon.actors.genie import Genie
from assets import load as use_assets
from lib.sprite import Sprite
from config import TILE_SIZE
from random import randint, randrange, choice
from colors.palette import WHITE, SEAGREEN, GREEN
from lib.filters import replace_color
from lib.cell import neighborhood
from contexts.dialogue import DialogueContext
from contexts.prompt import PromptContext, Choice
from contexts.save import SaveContext

class OasisRoom(SpecialRoom):
  shapes = [
    [
      "#...#",
      ".....",
      ".OVO.",
      ".OOO.",
      ".OOO.",
      ".....",
      "#...#"
    ], [
      ".........",
      "...OOOVO.",
      "...OOOOO.",
      ".........",
    ]
  ]

  scripts = [
    ("save", lambda game: DialogueContext(script=[
      lambda: PromptContext(
        message="{}: Save your game?".format(game.talkee.name.upper()),
        choices=[
          Choice("Yes"),
          Choice("No", closing=True),
        ],
        on_close=lambda choice: (
          choice.text == "Yes" and [
            lambda: SaveContext(data=game.get_head().child.save())
          ]
        )
      )
    ]))
  ]

  def __init__(room, shape_index=None, degree=1, *args, **kwargs):
    if shape_index is None:
      shape_index = randrange(len(OasisRoom.shapes))
    super().__init__(
      degree=degree,
      shape=OasisRoom.shapes[shape_index],
      *args, **kwargs
    )
    room.shape_index = shape_index

  def encode(room):
    cell, name, *props = super().encode()
    props = {
      **(props and props[0] or {}),
      "shape_index": room.shape_index,
    }
    return [cell, name, *(props and [props] or [])]

  def get_cells(room):
    return [c for c in super().get_cells() if c not in room.get_corners()]

  def get_border(room):
    return super().get_border() + room.get_corners()

  def get_edges(room):
    x, y = room.cell or (0, 0)
    width, height = room.size
    return [
      (x + width // 2, y - 2),
      (x + width // 2, y - 1),
      (x + width // 2, y + height + 1),
      (x + width // 2, y + height + 2),
      (x - 1, y + height // 2),
      (x + width, y + height // 2),
    ]

  def place(room, stage, cell=None, connectors=[]):
    if not super().place(stage, cell, connectors):
      return False
    sprites = use_assets().sprites
    room.cell = cell or room.cell or (0, 0)
    offset_x, offset_y = room.cell

    floor_cells = []
    oasis_cells = []
    for row in range(room.get_height()):
      for col in range(room.get_width()):
        cell = (col + offset_x, row + offset_y)
        char = room.shape[row][col]
        if SpecialRoom.parse_char(char) is stage.FLOOR:
          floor_cells.append(cell)
        if SpecialRoom.parse_char(char) is stage.OASIS:
          oasis_cells.append(cell)

    for i in range(randint(2, 3)):
      cell = choice(floor_cells)
      floor_cells.remove(cell)
      stage.spawn_elem_at(cell, Palm())

    for i in range(8):
      cell = choice(floor_cells)
      floor_cells.remove(cell)
      x, y = cell
      for j in range(2):
        for k in range(2):
          if randint(1, 5) == 1:
            offset_x = j * 16
            offset_y = k * 16
            stage.decors.append(Decor(
              kind="oasis_grass",
              cell=cell,
              offset=(offset_x, offset_y),
              color=SEAGREEN
            ))

    wave_decors = []
    while oasis_cells:
      cell = choice(oasis_cells)
      oasis_cells.remove(cell)
      x, y = cell
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
      if (not corners
      or len(wave_decors) >= 3 and randint(0, 1)):
        continue
      corner_x, corner_y = choice(corners)
      offset_x = corner_x * 16
      offset_y = corner_y * 16
      wave_decors.append(Decor(
        kind=choice(("oasis_wave", "oasis_waves")),
        cell=cell,
        offset=(offset_x, offset_y)
      ))
    stage.decors += wave_decors

    # actor_cells = room.get_corners()
    # if stage.get_tile_at(actor_cells[0]) is stage.WALL:
    #   actor_cells = [n for ns in [neighborhood(c) for c in room.get_corners()] for n in ns if n not in room.get_border()]
    # actor_cell = choice(actor_cells)
    # stage.spawn_elem_at(actor_cell, Genie(
    #   name="Eljin",
    #   color=GREEN,
    #   message=next((s for s in OasisRoom.scripts if s[0] == "save"), None)
    # ))

    return True
