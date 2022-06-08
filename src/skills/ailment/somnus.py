import lib.vector as vector
from lib.cell import is_adjacent

from skills.ailment import AilmentSkill
from anims.attack import AttackAnim
from anims.pause import PauseAnim
from config import ATTACK_DURATION

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
      AttackAnim(
        duration=ATTACK_DURATION,
        target=user,
        src=user.cell,
        dest=target_cell,
        on_start=on_start,
        on_end=on_attack_end
      )
    ])

    return target_cell
