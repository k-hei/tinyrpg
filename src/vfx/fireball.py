from vfx import Vfx
from config import TILE_SIZE

class Fireball(Vfx):
  def find_end_angle(start_angle, target_cell):
    col, row = target_cell
    x, y = col * TILE_SIZE, row * TILE_SIZE

  def __init__(fx, pos, target_cell, start_angle):
    super().__init__()
    fx.pos = pos
    fx.target_cell = target_cell
    fx.start_angle = start_angle
    fx.end_angle = Fireball.find_end_angle(start_angle, target_cell)

  def update(fx):
    pass
