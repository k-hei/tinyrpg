from dungeon.element import DungeonElement
from dungeon.props.puzzledoor import PuzzleDoor
from assets import load as use_assets
from filters import replace_color
from colors.palette import BLACK, WHITE, GRAY, PURPLE, DARKGRAY, DARKBLUE
from sprite import Sprite
from anims.pause import PauseAnim

class PushTile(DungeonElement):
  def __init__(tile, pushed=False, completed=False):
    super().__init__(solid=False)
    tile.pushed = pushed
    tile.completed = completed

  def effect(tile, game, *_):
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

  def on_leave(tile, game):
    if not tile.completed:
      tile.pushed = False

  def view(tile, anims):
    assets = use_assets()
    tile_image = assets.sprites["push_tile"]
    tile_image = replace_color(tile_image, GRAY, DARKGRAY)
    if tile.pushed:
      tile_image = replace_color(tile_image, WHITE, PURPLE)
      tile_image = replace_color(tile_image, BLACK, DARKBLUE)
    return super().view(Sprite(
      image=tile_image,
      layer="decors"
    ), anims)

  def encode(tile):
    [cell, kind, *props] = super().encode()
    props = {
      **(props[0] if props else {}),
      **(tile.pushed and { "pushed": True } or {}),
      **(tile.completed and { "completed": True } or {}),
    }
    return [cell, kind, *(props and [props] or [])]
