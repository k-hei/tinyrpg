import lib.vector as vector
from dungeon.actors import DungeonActor
from cores.attendant import AttendantCore
from colors.palette import ORANGE
from config import TILE_SIZE


class Attendant(DungeonActor):
  def __init__(attendant, *args, **kwargs):
    super().__init__(
      core=AttendantCore(color=ORANGE, *args, **kwargs),
    )

  def spawn(elem, stage, cell):
    elem.scale = TILE_SIZE
    elem.cell = vector.scale(cell, stage.tile_size / TILE_SIZE)

  def view(attendant, anims=[]):
    return super().view(attendant.core.view(), anims)
