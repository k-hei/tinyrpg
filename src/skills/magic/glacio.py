from random import randint
from skills.magic import MagicSkill
from cores.mage import Mage
from dungeon.actors import DungeonActor
from config import TILE_SIZE, ATTACK_DURATION
from anims.attack import AttackAnim
from anims.frame import FrameAnim
from anims.pause import PauseAnim
from vfx.icespike import IceSpikeVfx
from colors.palette import CYAN
from config import ENABLED_COMBAT_LOG

class Glacio(MagicSkill):
  name = "Glacio"
  kind = "magic"
  element = "ice"
  desc = "Freezes target with ice"
  cost = 4
  range_max = 4
  atk = 1
  users = [Mage]
  blocks = (
    (0, 0),
    (1, 0),
  )

  def effect(user, dest, game, on_end=None):
    camera = game.camera
    floor = game.floor
    hero_x, hero_y = user.cell
    delta_x, delta_y = user.facing
    bump_dest = (hero_x + delta_x, hero_y + delta_y)

    if dest is None:
      dest = Glacio().find_targets(user, game.floor)[-1]
    target = floor.get_elem_at(dest, superclass=DungeonActor)
    target_cells = []
    cell = user.cell
    dist = 0
    while cell != dest and dist < Glacio.range_max:
      x, y = cell
      cell = (x + delta_x, y + delta_y)
      target_cells.append(cell)
      dist += 1

    def on_connect():
      damage = 8 + randint(-2, 2)
      block = game.can_block(attacker=user, defender=target)
      if block:
        target.block()
        damage /= 2
      game.flinch(
        target=target,
        damage=damage,
        on_end=lambda: (
          not block and game.freeze(target),
          game.anims[0].append(PauseAnim(
            duration=30,
            on_end=on_end
          ))
        )
      )

    def on_bump():
      game.vfx += [IceSpikeVfx(
        cell=cell,
        delay=i * 10,
        color=CYAN,
        on_connect=target and cell == target_cells[-1] and on_connect
      ) for i, cell in enumerate(target_cells)]

    def on_bump_end():
      delay = len(target_cells) * 10 + 10
      game.anims[0].append(PauseAnim(
        duration=15 + delay,
        on_end=lambda: (
          ENABLED_COMBAT_LOG and game.log.print("But nothing happened..."),
          game.anims[0].append(PauseAnim(
            duration=30,
            on_end=on_end
          ))
        )
      ))

    game.anims.append([AttackAnim(
      duration=ATTACK_DURATION,
      target=user,
      src=user.cell,
      dest=bump_dest,
      on_connect=on_bump,
      on_end=target is None and on_bump_end
    )])

    return dest
