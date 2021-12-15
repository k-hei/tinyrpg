from random import random, randint, shuffle
from lib.compose import compose

from skills.magic import MagicSkill
from cores.mage import Mage
from dungeon.actors import DungeonActor
from dungeon.stage import Tile
from anims.attack import AttackAnim
from anims.frame import FrameAnim
from anims.pause import PauseAnim
from vfx.iceemblem import IceEmblemVfx
from vfx.icespike import IceSpikeVfx
from vfx.snowflake import SnowflakeVfx
from vfx.particle import ParticleVfx
from vfx.smoke import SmokeVfx
from vfx.magiccircle import MagicCircleVfx
from colors.palette import CYAN
from config import TILE_SIZE, ATTACK_DURATION, ENABLED_COMBAT_LOG

class Congelatio(MagicSkill):
  name = "Congelatio"
  kind = "magic"
  element = "ice"
  desc = "Freezes targets with blizzard"
  cost = 6
  range_type = "radial"
  range_min = 2
  range_max = 3
  range_radius = 1
  atk = 1
  charge_turns = 2
  users = [Mage]
  blocks = (
    (1, 0),
    (0, 1),
    (1, 1),
    (2, 1),
    (1, 2),
  )

  def effect(user, dest, game, on_end=None):
    floor = game.stage
    hero_x, hero_y = user.cell
    delta_x, delta_y = user.facing
    bump_dest = (hero_x + delta_x, hero_y + delta_y)
    target_cells = Congelatio().find_targets(user, floor, dest)
    target_cells = [c for c in target_cells if (
      not Tile.is_solid(floor.get_tile_at(c))
      and not next((e for e in floor.get_elems_at(c) if not isinstance(e, DungeonActor) and e.solid), None)
      and not (user.faction == "player" and c not in game.hero.visible_cells)
    )]
    target_cells = sorted(target_cells, key=lambda cell: 0 if cell == dest else 1 + random())
    targets = [e for c in target_cells for e in floor.get_elems_at(c) if e and isinstance(e, DungeonActor)]

    pause_anim = PauseAnim()
    def on_connect():
      game.vfx.extend([
        MagicCircleVfx(cell=dest),
        *[(lambda cell, target: IceSpikeVfx(
          cell=cell,
          delay=i * 5 + 45,
          color=CYAN,
          on_connect=(lambda: (
            not pause_anim.done and (
              pause_anim.end(),
              game.vfx.extend([
                SnowflakeVfx(cell=dest),
                *([SmokeVfx(cell=dest) for _ in range(20)]),
                *([ParticleVfx(cell=dest, linger=True) for _ in range(40)]),
              ])
            ),
            target.inflict_ailment("freeze"),
            game.flinch(
              target=target,
              damage=8 + randint(-2, 2),
              on_end=lambda: (
                game.inflict_freeze(target),
                game.anims[0].append(PauseAnim(
                  duration=30,
                  on_end=on_end
                ))
              )
            )
          )) if target in targets else None
        ))(
          cell,
          target=next((e for e in floor.get_elems_at(cell) if isinstance(e, DungeonActor)), None)
        ) for i, cell in enumerate(target_cells)]
      ])
      if not targets:
        pause_anim.end()
        game.anims.append([PauseAnim(
          duration=120,
          on_end=on_end
        )])

    user.core.anims.append(Mage.CastAnim())
    game.vfx.extend([IceEmblemVfx(cell=user.cell, delay=15)])

    on_end = compose(on_end, game.undarken)
    game.anims.extend([
      [PauseAnim(duration=90, on_end=lambda: user.core.anims.pop())],
      [AttackAnim(
        duration=ATTACK_DURATION,
        target=user,
        src=user.cell,
        dest=bump_dest,
        on_start=lambda: (
          game.darken(),
          game.display_skill(Congelatio, user),
        ),
        on_connect=on_connect
      ), pause_anim]
    ])
