from random import randint, choice
from dungeon.actors import DungeonActor
from cores.beetle import Beetle as BeetleCore
from items.materials.beetle import Beetle as BeetleItem
from anims.item import ItemAnim
from anims.pause import PauseAnim
from contexts.dialogue import DialogueContext
from lib.sprite import Sprite
from config import ATTACK_DURATION

class Beetle(DungeonActor):
  def __init__(beetle, *args, **kwargs):
    super().__init__(BeetleCore(), behavior="flee", *args, **kwargs)

  def step(beetle, game):
    enemy = game.hero
    if enemy is None:
      return None
    beetle_x, beetle_y = beetle.cell
    enemy_x, enemy_y = enemy.cell
    dist_x = enemy_x - beetle_x
    delta_x = dist_x // (abs(dist_x) or 1)
    dist_y = enemy_y - beetle_y
    delta_y = dist_y // (abs(dist_y) or 1)
    delta = None
    if abs(dist_x) + abs(dist_y) == 1:
      if game.floor.is_cell_empty((beetle_x - delta_x, beetle_y - delta_y)):
        delta = (-delta_x, -delta_y)
      else:
        deltas = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        deltas = [(dx, dy) for (dx, dy) in deltas if game.floor.is_cell_empty((beetle_x + dx, beetle_y + dy))]
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

  def effect(beetle, game):
    if beetle.is_immobile():
      return None
    game.anims.append([
      PauseAnim(
        duration=ATTACK_DURATION // 2,
        on_end=lambda: game.floor.remove_elem(beetle)
      ),
      item_anim := ItemAnim(
        target=game.hero,
        item=BeetleItem()
      )
    ])
    game.store.obtain(BeetleItem)
    game.open(child=DialogueContext(
      lite=True,
      script=[("", ("Obtained ", BeetleItem().token(), "."))]
    ), on_close=lambda: item_anim and item_anim.end())

  def view(beetle, anims=[]):
    return super().view(beetle.core.view(anims and [a for a in anims[0] if a.target is beetle]), anims)
