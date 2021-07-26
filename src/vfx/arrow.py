from vfx import Vfx

class Arrow(Vfx):
  def __init__(arrow, cell, direction, *args, **kwargs):
    super().__init__(*args, **kwargs)
    arrow.cell = cell
    arrow.direction = direction
