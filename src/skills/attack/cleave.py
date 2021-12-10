from random import randint
from skills.attack import AttackSkill
from anims.attack import AttackAnim
from anims.pause import PauseAnim
from anims.frame import FrameAnim
from dungeon.actors import DungeonActor
from cores.knight import Knight as Knight
from vfx.impact import ImpactVfx
from config import TILE_SIZE, ENABLED_COMBAT_LOG

class Cleave(AttackSkill):
  name = "Cleave"
  desc = "Slash with increased power"
  element = "sword"
  cost = 3
  users = [Knight]
  blocks = (
    (1, 0),
    (0, 1),
    (1, 1),
    (2, 1),
  )

  def effect(user, dest, game, on_end=None):
    floor = game.stage
    hero_x, hero_y = user.cell
    delta_x, delta_y = user.facing
    target_cell = (hero_x + delta_x, hero_y + delta_y)
    target_elem = floor.get_elem_at(target_cell, superclass=DungeonActor)

    def on_connect():
      game.vfx.append(ImpactVfx(cell=target_cell))

    def on_pause():
      game.flinch(
        target=target_elem,
        damage=game.find_damage(user, target_elem, 1.25),
        on_end=on_end
      )

    def on_bump():
      if target_elem:
        game.anims[0].append(PauseAnim(
          duration=45,
          on_end=on_pause
        ))
      else:
        game.anims[0].append(PauseAnim(
          duration=45,
          on_end=lambda: (
            ENABLED_COMBAT_LOG and game.log.print("But nothing happened..."),
            on_end and on_end()
          )
        ))

    game.anims.append([AttackAnim(
      target=user,
      src=user.cell,
      dest=target_cell,
      on_connect=on_connect,
      on_end=on_bump
    )])

    return target_cell
