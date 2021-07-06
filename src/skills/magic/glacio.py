from random import randint
from skills import find_skill_targets
from skills.magic import MagicSkill
from cores.mage import Mage
from dungeon.actors import DungeonActor
from config import TILE_SIZE, ATTACK_DURATION
from anims.attack import AttackAnim
from anims.frame import FrameAnim
from anims.pause import PauseAnim
from vfx.icespike import IceSpikeVfx
from palette import CYAN

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

    if not dest:
      dest = find_skill_targets(Glacio, user, game.floor)[-1]
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
      game.vfx += [IceSpikeVfx(
        cell=cell,
        delay=i * 10,
        color=CYAN
      ) for i, cell in enumerate(target_cells)]

    def on_bump():
      delay = len(target_cells) * 10 + 10
      if target is None:
        game.anims[0].append(PauseAnim(
          duration=15 + delay,
          on_end=lambda: (
            game.log.print("But nothing happened..."),
            on_end and on_end()
          )
        ))
      else:
        game.anims[0].append(PauseAnim(
          duration=delay,
          on_end=lambda: (
            target.inflict_ailment("freeze"),
            game.flinch(
              target=target,
              damage=8 + randint(-2, 2),
              on_end=lambda: (
                not target.is_dead() and game.log.print((target.token(), " is frozen.")),
                on_end and on_end()
              )
            )
          )
        ))

    game.anims.append([AttackAnim(
      duration=ATTACK_DURATION,
      target=user,
      src=user.cell,
      dest=bump_dest,
      on_connect=on_connect,
      on_end=on_bump
    )])

    return dest
