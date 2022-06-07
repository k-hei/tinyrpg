from pygame import Rect
from dataclasses import dataclass
from dungeon.props import Prop
import assets, trace
from anims.frame import FrameAnim
from colors.palette import WHITE, DARKBLUE
import lib.vector as vector
from lib.filters import replace_color
from lib.sprite import Sprite
from config import TILE_SIZE
# from dungeon.stage import Stage, Tile

@dataclass
class SpriteMap:
  closed: str
  opened: str
  opening_frames: list[str]

class Door(Prop):
  solid = True
  static = True
  active = True
  sprites = SpriteMap(
    closed="door_puzzle",
    opened="door_puzzle_open",
    opening_frames=["door_puzzle", "door_puzzle_opening", "door_puzzle_open"]
  )

  def __init__(door, opened=False, locked=None):
    super().__init__(solid=(not opened), opaque=(not opened))
    door.opened = opened
    door.locked = locked
    door.vertical = False
    door.focus = None
    door.origin = None
    if opened:
      door.open()

  @property
  def rect(door):
    if door._rect is None and door.pos:
      door._rect = Rect(
        vector.subtract(door.pos, (16, 16)),
        (32, 32)
      )
    return door._rect

  def encode(door):
    [cell, kind, *props] = super().encode()
    props = {
      **(props[0] if props else {}),
      **(door.opened and { "opened": True } or {}),
      **(door.locked and { "locked": True } or {}),
    }
    return [door.origin or cell, kind, *(props and [props] or [])]

  def unlock(door):
    if door.locked:
      door.locked = False

  def lock(door):
    door.locked = True

  def effect(door, game, *_):
    if door.locked:
      return game.comps.minilog.print("The door is locked...")
    return door.handle_open(game)

  # def spawn(door, stage, cell):
  #   super().spawn(stage, cell)
  #   door_x, door_y = cell
  #   door.origin = cell
  #   # if Tile.get_elev(stage.get_tile_at((door_x - 1, door_y))):
  #   #   door.elev += 1
  #   # if (Tile.is_solid(stage.get_tile_at((door_x - 1, door_y)))
  #   # and Tile.is_solid(stage.get_tile_at((door_x + 1, door_y)))
  #   # and Tile.is_solid(stage.get_tile_at((door_x - 1, door_y + 1)))
  #   # and Tile.is_solid(stage.get_tile_at((door_x + 1, door_y + 1)))):
  #   #   door.vertical = True

  def open(door):
    door.solid = False
    door.opened = True
    door.opaque = False
    door.active = False
    if door.locked:
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
    not game.anims and game.anims.append([])
    game.anims[0].append(anim)
    return True

  def close(door, lock=True):
    door.solid = True
    door.opened = False
    door.locked = lock
    door.active = True

  def handle_close(door, game, lock=True):
    if door.opened:
      not game.anims and game.anims.append([])
      game.anims[0].append(DoorCloseAnim(
        target=door,
        duration=30,
        frames=list(reversed(door.sprites.opening_frames)),
      ))
    door.close(lock=lock)
    return True

  def align(door, game):
    door_x, door_y = door.cell
    origin_x, origin_y = door.origin
    focus_x, focus_y = door.focus or door.cell
    if not door.vertical or focus_y <= origin_y:
      door.cell = door.origin
    elif door.cell == door.origin:
      door.cell = (door_x, door_y + 1)

  def view(door, anims):
    will_open = next((a for g in anims for a in g if a.target is door and type(a) is DoorOpenAnim), None)
    will_close = next((a for g in anims for a in g if a.target is door and type(a) is DoorCloseAnim), None)
    anim_group = [a for a in anims[0] if a.target is door] if anims else []
    for anim in anim_group:
      if isinstance(anim, DoorAnim):
        image = assets.sprites[anim.frame()]
        break
    else:
      if door.opened or will_close:
        image = assets.sprites[door.sprites.opened]
      elif not door.opened or will_open:
        image = assets.sprites[door.sprites.closed]

    door_color = DARKBLUE if door.locked is False else door.color
    image = replace_color(image, WHITE, door_color)
    return super().view([Sprite(
      image=image,
      layer="decors"
    )], anims)

class DoorAnim(FrameAnim): pass
class DoorOpenAnim(DoorAnim): pass
class DoorCloseAnim(DoorAnim): pass
