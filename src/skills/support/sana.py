from config import ATTACK_DURATION
from skills.support import SupportSkill
from anims.attack import AttackAnim
from anims.pause import PauseAnim
from comps.damage import DamageValue
import palette
import random

from dungeon.actors import DungeonActor
from cores.mage import MageCore

class Sana(SupportSkill):
  name = "Sana"
  desc = "Restores HP slightly"
  cost = 3
  range_min = 0
  range_max = 1
  users = (MageCore,)
  blocks = (
    (1, 0),
    (0, 1),
    (1, 1),
    (0, 2),
  )

  def effect(user, dest, game, on_end=None):
    source_cell = user.cell
    hero_x, hero_y = source_cell
    delta_x, delta_y = user.facing
    target_cell = (hero_x + delta_x, hero_y + delta_y)
    target_elem = game.floor.get_elem_at(target_cell)
    def on_attack_end():
      if target_elem:
        amount = 20 + random.randint(-2, 2)
        target_elem.regen(amount)
        game.numbers.append(DamageValue(str(amount), target_cell, palette.GREEN))
        result = (target_elem.token(), " restored ", str(amount), " HP.")
      else:
        result = "But nothing happened..."
      game.anims[0].append(PauseAnim(
        duration=30,
        on_end=lambda: (
          game.log.print(result),
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
        src_cell=user.cell,
        dest_cell=target_cell,
        on_end=on_attack_end
      )
    ])
    return target_cell
