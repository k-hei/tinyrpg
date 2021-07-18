from random import random, randint, shuffle
from skills.magic import MagicSkill
from cores.mage import Mage
from dungeon.actors import DungeonActor
from config import TILE_SIZE, ATTACK_DURATION
from anims.attack import AttackAnim
from anims.frame import FrameAnim
from anims.pause import PauseAnim
from vfx.icespike import IceSpikeVfx
from colors.palette import CYAN

class Congelatio(MagicSkill):
  name = "Congelatio"
  kind = "magic"
  element = "ice"
  desc = "Freezes targets with blizzard"
  cost = 12
  range_type = "radial"
  range_min = 2
  range_max = 3
  range_radius = 1
  atk = 1
  chant_turns = 2
  users = [Mage]
  blocks = (
    (1, 0),
    (0, 1),
    (1, 1),
    (2, 1),
  )

  def effect(user, dest, game, on_end=None):
    floor = game.floor
    hero_x, hero_y = user.cell
    delta_x, delta_y = user.facing
    bump_dest = (hero_x + delta_x, hero_y + delta_y)
    target_cells = Congelatio().find_targets(user, floor, dest)
    target_cells = sorted(target_cells, key=lambda cell: 0 if cell == dest else 1 + random())
    targets = [e for e in [floor.get_elem_at(c, superclass=DungeonActor) for c in target_cells] if e]

    def on_connect():
      game.vfx += [(lambda cell, target: IceSpikeVfx(
        cell=cell,
        delay=i * 5,
        color=CYAN,
        on_connect=(lambda: (
          target.inflict_ailment("freeze"),
          game.flinch(
            target=target,
            damage=8 + randint(-2, 2),
            on_end=lambda: (
              game.freeze(target),
              game.anims[0].append(PauseAnim(
                duration=45,
                on_end=on_end
              ))
            )
          )
        )) if target in targets else None
      ))(cell, target=floor.get_elem_at(cell)) for i, cell in enumerate(target_cells)]
      if not targets:
        game.anims[0].append(PauseAnim(
          duration=60,
          on_end=lambda: (
            game.log.print("But nothing happened..."),
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
      on_connect=on_connect
    )])

    return dest
