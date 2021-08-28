from random import randint, choice
from dungeon.actors import DungeonActor
from cores.bug import Bug as BugCore
from items.materials.bug import Bug as BugItem
from anims.item import ItemAnim
from anims.pause import PauseAnim
from contexts.dialogue import DialogueContext
from sprite import Sprite
from config import ATTACK_DURATION

class Bug(DungeonActor):
  def __init__(bug, *args, **kwargs):
    super().__init__(BugCore(), *args, **kwargs)

  def step(bug, game):
    enemy = game.hero
    if enemy is None:
      return None
    bug_x, bug_y = bug.cell
    enemy_x, enemy_y = enemy.cell
    dist_x = enemy_x - bug_x
    delta_x = dist_x // (abs(dist_x) or 1)
    dist_y = enemy_y - bug_y
    delta_y = dist_y // (abs(dist_y) or 1)
    delta = None
    if abs(dist_x) + abs(dist_y) == 1:
      if game.floor.is_cell_empty((bug_x - delta_x, bug_y - delta_y)):
        delta = (-delta_x, -delta_y)
      else:
        deltas = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        deltas = [(dx, dy) for (dx, dy) in deltas if game.floor.is_cell_empty((bug_x + dx, bug_y + dy))]
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

  def effect(bug, game):
    if bug.is_immobile():
      return None
    game.anims.append([
      PauseAnim(
        duration=ATTACK_DURATION // 2,
        on_end=lambda: game.floor.remove_elem(bug)
      ),
      item_anim := ItemAnim(
        target=game.hero,
        item=BugItem()
      )
    ])
    game.store.obtain(BugItem)
    game.open(child=DialogueContext(
      lite=True,
      script=[("", ("Obtained ", BugItem().token(), "."))]
    ), on_close=lambda: item_anim and item_anim.end())

  def view(bug, anims=[]):
    return super().view(bug.core.view(anims and [a for a in anims[0] if a.target is bug]), anims)
