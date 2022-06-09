from random import random
import lib.vector as vector
from lib.cell import is_adjacent

from skills.ailment import AilmentSkill
from anims.ripple import RippleAnim
from anims.pause import PauseAnim

from dungeon.actors import DungeonActor
from cores.mage import Mage


class Somnus(AilmentSkill):
  name = "Somnus"
  kind = "ailment"
  element = "dark"
  desc = "Lulls target to sleep"
  cost = 3
  users = (Mage,)
  blocks = (
    (0, 0),
    (0, 1),
  )

  def effect(game, user, dest=None, on_start=None, on_end=None):
    target = dest
    if isinstance(target, DungeonActor):
      target_cell = target.cell
      user.face(target_cell)
    else:
      target_cell = dest

    if not target_cell or not is_adjacent(user.cell, target_cell):
      target_cell = vector.add(user.cell, user.facing)

    target_elem = next((e for e in game.stage.get_elems_at(target_cell)
      if isinstance(e, DungeonActor)), None)

    def on_attack_end():
      if target_elem:
        if random() < 1 / 5:
          result = (target_elem.token(), " was unaffected.")
        else:
          target_elem.inflict_ailment("sleep")
          result = (target_elem.token(), " fell asleep!")
      else:
        result = "But nothing happened..."

      game.anims[0].append(PauseAnim(
        duration=30,
        on_end=lambda: (
          game.print(result),
          game.anims[0].append(PauseAnim(
            duration=30,
            on_end=on_end
          ))
        )
      ))

    game.anims.append([
      RippleAnim(
        duration=120,
        target=user,
        on_start=lambda: on_start and on_start(user.cell),
        on_end=on_attack_end
      )
    ])

    return target_cell
