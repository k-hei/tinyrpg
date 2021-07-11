from dungeon.element import DungeonElement
from dungeon.props.puzzledoor import PuzzleDoor
from assets import load as use_assets
from filters import replace_color
from palette import BLACK, WHITE, GRAY, PURPLE, GRAY_DARK, BLUE_DARK
from sprite import Sprite
from anims.pause import PauseAnim

class PushTile(DungeonElement):
  def __init__(tile):
    super().__init__(solid=False)
    tile.pushed = False
    tile.completed = False

  def effect(tile, game):
    tile.pushed = True
    pushtiles = []
    for cell in game.room.get_cells():
      pushtile = game.floor.get_elem_at(cell, superclass=PushTile)
      if pushtile:
        pushtiles.append(pushtile)
    if not tile.completed and len([t for t in pushtiles if t.pushed]) == len(pushtiles):
      for t in pushtiles:
        tile.completed = True
      door = None
      for cell in game.room.get_border():
        door = game.floor.get_elem_at(cell, superclass=PuzzleDoor)
        if door:
          door.unlock()
          game.anims.append([PauseAnim(
            duration=60,
            on_end=lambda: door.effect(game)
          )])
          break

  def aftereffect(tile, game):
    if not tile.completed:
      tile.pushed = False

  def view(tile, anims):
    assets = use_assets()
    tile_image = assets.sprites["push_tile"]
    tile_image = replace_color(tile_image, GRAY, GRAY_DARK)
    if tile.pushed:
      tile_image = replace_color(tile_image, WHITE, PURPLE)
      tile_image = replace_color(tile_image, BLACK, BLUE_DARK)
    return super().view(Sprite(
      image=tile_image,
      layer="decors"
    ), anims)
