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

  def effect(user, dest, game, on_end=None):
    source_cell = user.cell
    hero_x, hero_y = source_cell
    delta_x, delta_y = user.facing
    target_cell = (hero_x + delta_x, hero_y + delta_y)
    target_elem = game.stage.get_elem_at(target_cell)
    def on_attack_end():
      if target_elem:
        target_elem.inflict_ailment("sleep")
        if type(target_elem) is DungeonActor and target_elem.idle:
          target_elem.activate()
        result = (target_elem.token(), " fell asleep!")
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
        src=user.cell,
        dest=target_cell,
        on_end=on_attack_end
      )
    ])
    return target_cell
