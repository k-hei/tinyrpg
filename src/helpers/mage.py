from random import randint, choice
import assets
from anims.step import StepAnim
from anims.path import PathAnim
from anims.jump import JumpAnim
from anims.attack import AttackAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from anims.shake import ShakeAnim
from anims.drop import DropAnim
from anims.fall import FallAnim
from anims.walk import WalkAnim
from dungeon.actors import DungeonActor

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
    if game.stage.is_cell_empty((mage_x - delta_x, mage_y - delta_y)):
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

  if delta:
    return ("move", delta)

def view_mage(mage, anims):
  sprites = assets.sprites
  anim_group = [a for a in anims[0] if a.target is mage] if anims else []
  anim_group += mage.core.anims
  will_fall = anims and next((a for a in anims[0] if type(a) is FallAnim), None)
  if will_fall and anims[0].index(will_fall) > 0:
    return DungeonActor.view(mage, sprites["mage_shock"], anims)
  for anim in anim_group:
    if isinstance(anim, (StepAnim, PathAnim, WalkAnim)):
      x4_idx = max(0, int((anim.time - 1) % anim.period // (anim.period / 4)))
      if mage.facing == (0, -1):
        sprite = [
          sprites["mage_up"],
          sprites["mage_walkup0"],
          sprites["mage_up"],
          sprites["mage_walkup1"]
        ][x4_idx]
        break
      elif mage.facing == (0, 1):
        sprite = [
          sprites["mage_down"],
          sprites["mage_walkdown0"],
          sprites["mage_down"],
          sprites["mage_walkdown1"]
        ][x4_idx]
        break
      elif anim.time % (anim.period // 2) >= anim.period // 4:
        sprite = sprites["mage_walk"]
        break
    elif type(anim) is JumpAnim:
      if mage.facing == (0, -1):
        sprite = sprites["mage_walkup"]
      elif mage.facing == (0, 1):
        sprite = sprites["mage_walkdown"]
      else:
        sprite = sprites["mage_walk"]
      break
    elif (type(anim) is AttackAnim
    and anim.time < anim.duration // 2):
      if mage.facing == (0, -1):
        sprite = sprites["mage_walkup"]
      elif mage.facing == (0, 1):
        sprite = sprites["mage_walkdown"]
      else:
        sprite = sprites["mage_walk"]
      break
    elif type(anim) in (FlinchAnim, FlickerAnim, DropAnim):
      sprite = sprites["mage_flinch"]
      break
    elif type(anim) is ShakeAnim:
      sprite = sprites["mage_shock"]
      break
    elif type(anim) is FallAnim:
      sprite = sprites["mage_flinch"]
      break
  else:
    if mage.facing == (0, -1):
      sprite = sprites["mage_up"]
    elif mage.facing == (0, 1):
      sprite = sprites["mage_down"]
    else:
      sprite = sprites["mage"]

  return DungeonActor.view(mage, sprite, anims)
