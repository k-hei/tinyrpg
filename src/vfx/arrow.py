import lib.vector as vector
from random import randint
from pygame.transform import flip
from lib.sprite import Sprite
from vfx import Vfx
import assets
from lib.filters import replace_color
from anims.frame import FrameAnim
from anims.flinch import FlinchAnim
from dungeon.actors import DungeonActor
from colors.palette import BLACK, RED
from config import TILE_SIZE

def snap(pos, scale):
  x, y = pos
  return (int(x // scale), int(y // scale))

def get_arrow_frames(direction):
  if direction == (-1, 0):
    frames = [flip(s, True, False) for s in assets.sprites["arrow_right"]]
  elif direction == (1, 0):
    frames = assets.sprites["arrow_right"]
  elif direction == (0, -1):
    frames = assets.sprites["arrow_up"]
  elif direction == (0, 1):
    frames = assets.sprites["arrow_down"]
  return [replace_color(f, BLACK, RED) for f in frames]

class ArrowAnim(FrameAnim):
  frames_duration = 5
  loop = True

class ArrowLeftAnim(ArrowAnim): frames = get_arrow_frames((-1, 0))
class ArrowRightAnim(ArrowAnim): frames = get_arrow_frames((1, 0))
class ArrowUpAnim(ArrowAnim): frames = get_arrow_frames((0, -1))
class ArrowDownAnim(ArrowAnim): frames = get_arrow_frames((0, 1))

class Arrow(Vfx):
  speed = 5

  def __init__(arrow, cell, direction, *args, **kwargs):
    super().__init__(pos=vector.add(
      vector.scale(
        vector.add(cell, (0.5, 0.5), vector.scale(direction, 0.5)),
        scalar=TILE_SIZE
      ),
      direction[0] and (0, -6) or (0, 0)
    ), *args, **kwargs)
    arrow.direction = direction
    arrow.elev = 0
    arrow.anim = {
      (-1, 0): ArrowLeftAnim(),
      (1, 0): ArrowRightAnim(),
      (0, -1): ArrowUpAnim(),
      (0, 1): ArrowDownAnim(),
    }[direction]

  @property
  def facing(arrow):
    return arrow.direction

  def update(arrow, game):
    if arrow.done:
      return

    arrow.pos = vector.add(arrow.pos, vector.scale(arrow.direction, arrow.speed))
    arrow.anim.update()
    arrow_cell = snap(arrow.pos, TILE_SIZE)
    next_cell = vector.add(arrow_cell, vector.scale(arrow.direction, scalar=2))
    hero = game.hero
    can_block = game.can_block(defender=hero, attacker=arrow)

    if next_cell == hero.cell and not game.anims:
      if can_block:
        hero.block()

    target_tile = game.stage.get_tile_at(arrow_cell)
    if target_tile and (not target_tile.solid and not abs(arrow.elev - target_tile.elev) >= 1 or target_tile is game.stage.PIT):
      target_tile = None
    target_elem = next((e for e in game.stage.get_elems_at(arrow_cell) if (
      e.solid
      and not (game.anims and next((a for a in game.anims[0] if type(a) is FlinchAnim and a.target is e), None))
    )), None)
    if target_tile or target_elem:
      arrow.done = True
      if not target_tile and target_elem and isinstance(target_elem, DungeonActor):
        if can_block:
          target_elem.block()
        game.nudge(target_elem, arrow.direction)
        game.flinch(target_elem,
          damage=0 if can_block else randint(4, 6),
          direction=arrow.direction
        )

  def view(arrow):
    return [Sprite(
      image=arrow.anim.frame(),
      pos=arrow.pos,
      origin=("center", "center"),
      layer="vfx"
    )]
