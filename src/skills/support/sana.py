import random
from skills.support import SupportSkill
from anims.attack import AttackAnim
from anims.pause import PauseAnim
from comps.damage import DamageValue
from colors.palette import GREEN

from dungeon.actors import DungeonActor
from cores.mage import Mage

class Sana(SupportSkill):
  name = "Sana"
  desc = "Restores HP slightly"
  cost = 3
  users = (Mage,)
  blocks = (
    (1, 0),
    (1, 1),
    (0, 1),
    (0, 2),
  )

  def effect(game, user, dest, on_start=None, on_end=None):
    source_cell = user.cell
    hero_x, hero_y = source_cell
    delta_x, delta_y = user.facing
    target_cell = (hero_x + delta_x, hero_y + delta_y)
    target_elem = next((e for e in game.stage.get_elems_at(target_cell)
      if isinstance(e, DungeonActor)), None)

    def on_attack_end():
      if target_elem:
        amount = 20 + random.randint(-2, 2)
        target_elem.regen(amount)
        game.numbers.append(DamageValue(
          text=str(amount),
          pos=target_elem.pos,
          color=GREEN
        ))
        result = (target_elem.token(), " restored ", str(amount), " HP.")
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
        target=user,
        src=user.cell,
        dest=target_cell,
        on_start=on_start,
        on_end=on_attack_end
      )
    ])

    return target_cell
