from random import randint
from skills.magic import MagicSkill
from cores.mage import Mage
from dungeon.actors import DungeonActor
from config import ATTACK_DURATION
from anims.attack import AttackAnim
from anims.frame import FrameAnim
from anims.pause import PauseAnim
from vfx.icespike import IceSpikeVfx
from vfx.iceemblem import IceEmblemVfx
from colors.palette import CYAN

class Glacio(MagicSkill):
  name = "Glacio"
  kind = "magic"
  element = "ice"
  desc = "Freezes target with ice"
  cost = 2
  range_max = 4
  atk = 1
  users = [Mage]
  blocks = (
    (0, 0),
    (1, 0),
  )

  def effect(game, user, dest=None, on_start=None, on_end=None):
    floor = game.stage
    hero_x, hero_y = user.cell
    delta_x, delta_y = user.facing
    bump_dest = (hero_x + delta_x, hero_y + delta_y)

    dest = Glacio().find_targets(user, game.stage)[-1]
    target = next((e for e in floor.get_elems_at(dest) if isinstance(e, DungeonActor)), None)
    target_cells = []
    cell = user.cell
    dist = 0
    while cell != dest and dist < Glacio.range_max:
      x, y = cell
      cell = (x + delta_x, y + delta_y)
      target_cells.append(cell)
      dist += 1

    pause_anim = PauseAnim()
    def on_connect():
      damage = 8 + randint(-2, 2)

      block = False
      # block = game.can_block(attacker=user, defender=target)
      # if block:
      #   target.block()
      #   damage /= 2

      pause_anim.end()
      game.inflict_freeze(target)
      game.flinch(
        target=target,
        damage=damage,
        animate=False,
        on_end=lambda: (
          game.anims[0].append(PauseAnim(
            duration=30,
            on_end=on_end
          ))
        )
      )

    def on_bump():
      game.vfx.extend([
        *[IceSpikeVfx(
          cell=cell,
          delay=i * 10,
          color=CYAN,
          on_connect=target and cell == target_cells[-1] and on_connect,
          on_end=not target and cell == target_cells[-1] and (lambda: (
            pause_anim.end(),
            on_end and on_end()
          ))
        ) for i, cell in enumerate(target_cells)]
      ])

    user.core.anims.append(Mage.CastAnim())
    game.vfx.extend([IceEmblemVfx(cell=user.cell, delay=15)])

    game.anims.extend([
      [PauseAnim(duration=90, on_end=lambda: user.core.anims.pop())],
      [AttackAnim(
        duration=ATTACK_DURATION,
        target=user,
        src=user.cell,
        dest=bump_dest,
        on_start=lambda: on_start and on_start(dest),
        on_connect=on_bump,
      ), pause_anim]
    ])

    return False
