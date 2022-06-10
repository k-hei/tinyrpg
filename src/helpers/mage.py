from random import randint, choice
import lib.vector as vector
from helpers.stage import is_cell_walkable_to_actor


def step_move(mage, game):
  enemy = game.find_closest_enemy(mage)
  if not enemy:
    return

  mage_x, mage_y = mage.cell
  enemy_x, enemy_y = enemy.cell
  dist_x = enemy_x - mage_x
  delta_x = dist_x // (abs(dist_x) or 1)
  dist_y = enemy_y - mage_y
  delta_y = dist_y // (abs(dist_y) or 1)

  delta = None
  if abs(dist_x) + abs(dist_y) == 1:
    target_cell = (mage_x - delta_x, mage_y - delta_y)
    if is_cell_walkable_to_actor(game.stage, target_cell, mage):
      delta = (-delta_x, -delta_y)
    else:
      deltas = [(-1, 0), (1, 0), (0, -1), (0, 1)]
      deltas = [(dx, dy) for (dx, dy) in deltas if game.stage.is_cell_empty((mage_x + dx, mage_y + dy))]
      if deltas:
        delta = choice(deltas)

  elif abs(dist_x) + abs(dist_y) < 4:
    if delta_x and delta_y:
      delta = randint(0, 1) and (-delta_x, 0) or (0, -delta_y)
    elif delta_x:
      delta = (-delta_x, 0)
    elif delta_y:
      delta = (0, -delta_y)

  else:
    if delta_x and delta_y:
      delta = randint(0, 1) and (delta_x, 0) or (0, delta_y)
    elif delta_x:
      delta = (delta_x, 0)
    elif delta_y:
      delta = (0, delta_y)

  # HACK: prevent auto-movement outside of room
  #       should ideally have a fallback
  if delta:
    target_cell = vector.add(mage.cell, delta)
    if game.room and target_cell not in game.room.cells:
      delta = None

  if delta:
    return ("move", delta)
