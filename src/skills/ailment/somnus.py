from random import random
from lib.cell import neighborhood

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
    elif isinstance(target, tuple):
      target_cell = target
      user.face(target_cell)

    target_cells = neighborhood(user.cell)
    target_elems = [e for c in target_cells
      for e in game.stage.get_elems_at(c)
        if isinstance(e, DungeonActor)]

    def on_effect():
      if not target_elems:
        result = "But nothing happened..."
      else:
        for elem in target_elems:
          # TODO: handle multiple
          if random() < 1 / 5:
            result = (elem.token(), " was unaffected.")
          else:
            elem.inflict_ailment("sleep")
            result = (elem.token(), " fell asleep!")

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
        on_end=on_effect
      )
    ])

    return user.cell
