from dataclasses import dataclass
from dungeon.props import Prop
from assets import load as use_assets
from anims.frame import FrameAnim
from palette import WHITE, SAFFRON
from filters import replace_color
from sprite import Sprite
from config import TILE_SIZE
from dungeon.stage import Stage, Tile

@dataclass
class SpriteMap:
  closed: str
  opened: str
  opening_frames: list[str]

class Door(Prop):
  sprites = SpriteMap(
    closed="door_puzzle",
    opened="door_puzzle_open",
    opening_frames=["door_puzzle", "door_puzzle_opening", "door_puzzle_open"]
  )

  def __init__(door, locked=False):
    super().__init__(solid=True, opaque=True)
    door.locked = locked
    door.opened = False
    door.vertical = False
    door.focus = None
    door.origin = None

  def unlock(door):
    door.locked = False

  def lock(door):
    door.locked = True

  def effect(door, game):
    if door.locked:
      return game.log.print("The door is locked...")
    door.handle_open(game)

  def spawn(door, stage, cell):
    super().spawn(stage, cell)
    door_x, door_y = cell
    door.origin = cell
    if (Tile.is_solid(stage.get_tile_at((door_x - 1, door_y)))
    and Tile.is_solid(stage.get_tile_at((door_x + 1, door_y)))
    and Tile.is_solid(stage.get_tile_at((door_x - 1, door_y + 1)))
    and Tile.is_solid(stage.get_tile_at((door_x + 1, door_y + 1)))):
      door.vertical = True

  def open(door):
    door.solid = False
    door.opened = True
    door.locked = False

  def handle_open(door, game):
    if door.opened:
      return False
    door.open()
    anim = DoorOpenAnim(
      duration=30,
      frames=door.sprites.opening_frames,
      target=door
    )
    if game.anims:
      game.anims[-1].append(anim)
    else:
      game.anims.append([anim])
    return True

  def close(door):
    door.solid = True
    door.opened = False
    door.locked = True

  def handle_close(door, game):
    if not door.opened:
      return False
    door.close()
    game.anims.append([
      DoorCloseAnim(
        duration=30,
        frames=list(reversed(door.sprites.opening_frames)),
        target=door
      )
    ])
    return True

  def view(door, anims):
    sprites = use_assets().sprites
    will_open = next((g for g in anims if next((a for a in g if a.target is door and type(a) is DoorOpenAnim), None)), None)
    will_close = next((g for g in anims if next((a for a in g if a.target is door and type(a) is DoorCloseAnim), None)), None)
    anim_group = [a for a in anims[0] if a.target is door] if anims else []
    door_x, door_y = door.cell
    origin_x, origin_y = door.origin
    focus_x, focus_y = door.focus or door.cell
    if not door.vertical or focus_y <= origin_y:
      door.cell = door.origin
    elif door.cell == door.origin:
      door.cell = (door_x, door_y + 1)
    for anim in anim_group:
      if isinstance(anim, DoorAnim):
        image = sprites[anim.frame]
        break
    else:
      if door.opened or will_close:
        image = sprites[door.sprites.opened]
      elif not door.opened or will_open:
        image = sprites[door.sprites.closed]
    image = replace_color(image, WHITE, SAFFRON)
    return [Sprite(
      image=image,
      layer="decors"
    )]

class DoorAnim(FrameAnim): pass
class DoorOpenAnim(DoorAnim): pass
class DoorCloseAnim(DoorAnim): pass
