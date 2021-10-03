from pygame import Rect
from dungeon.element import DungeonElement
from dungeon.actors import DungeonActor
from dungeon.props.door import Door
import assets
from sprite import Sprite
from lib.filters import replace_color
from anims.pause import PauseAnim
from colors.palette import BLACK, WHITE, GRAY, PURPLE, DARKGRAY, DARKBLUE
from config import PUSH_DURATION

class PushTile(DungeonElement):
  def __init__(tile, pushed=False, completed=False):
    super().__init__(solid=False)
    tile.pushed = pushed
    tile.completed = completed
    tile.sinking = False
    tile.anim = None

  def encode(tile):
    [cell, kind, *props] = super().encode()
    props = {
      **(props[0] if props else {}),
      **({ "pushed": True } if tile.pushed else {}),
      **({ "completed": True } if tile.completed else {}),
      **({ "sinking": tile.sinking } if tile.sinking else {}),
    }
    return [cell, kind, *(props and [props] or [])]

  def effect(tile, game, trigger):
    tile.pushed = True

    # find_pushblock(stage, cell)
    pushblock = trigger if not isinstance(trigger, DungeonActor) else None
    if pushblock:
      tile.anim = pushblock.SinkAnim(delay=PUSH_DURATION)
      tile.sinking = pushblock.SinkAnim.DEPTH

    # find_pushtiles(stage, room)
    pushtiles = []
    for cell in game.room.get_cells():
      pushtile = game.floor.get_elem_at(cell, superclass=PushTile)
      if pushtile:
        pushtiles.append(pushtile)

    # complete_puzzle(pushtiles)
    if not tile.completed and len([t for t in pushtiles if t.pushed]) == len(pushtiles):
      for t in pushtiles:
        tile.completed = True
      door = None
      for cell in game.room.get_edges():
        door = next((e for e in game.floor.get_elems_at(cell) if isinstance(e, Door) and not e.opened), None)
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

  def update(tile, *_):
    if not tile.anim:
      return
    if tile.anim.done:
      tile.anim = None
    else:
      tile.anim.update()

  def view(tile, anims):
    tile_yoffset = 0
    tile_image = assets.sprites["push_tile"]
    tile_image = replace_color(tile_image, GRAY, DARKGRAY)

    if tile.pushed:
      tile_image = replace_color(tile_image, DARKGRAY, PURPLE)
      tile_image = replace_color(tile_image, BLACK, DARKBLUE)
      tile_yoffset = 2

    if tile.anim and not tile.anim.bounces:
      tile_yoffset = tile.anim.z
    elif tile.sinking:
      tile_yoffset = tile.sinking

    if tile_yoffset:
      tile_image = tile_image.subsurface(Rect(
        (0, 0),
        (tile_image.get_width(), tile_image.get_height() - tile_yoffset)
      ))

    return super().view([Sprite(
      image=tile_image,
      layer="tiles"
    )], anims)
