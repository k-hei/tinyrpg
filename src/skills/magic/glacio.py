from random import randint
from skills.magic import MagicSkill
from cores.mage import Mage
from dungeon.actors import DungeonActor
from config import TILE_SIZE, ATTACK_DURATION
from anims.attack import AttackAnim
from anims.frame import FrameAnim
from anims.pause import PauseAnim
from vfx import Vfx
from palette import CYAN

class Glacio(MagicSkill):
  name = "Glacio"
  kind = "magic"
  element = "ice"
  desc = "Freezes target with ice"
  cost = 4
  range_max = 4
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

    target = floor.get_elem_at(dest, superclass=DungeonActor)
    target_cells = []
    cell = user.cell
    while cell != dest:
      x, y = cell
      cell = (x + delta_x, y + delta_y)
      target_cells.append(cell)

    def on_connect():
      impact_frames = ["fx_impact{}".format(i) for i in range(7)]
      game.vfx += [Vfx(
        kind="impact",
        pos=tuple([x * TILE_SIZE for x in cell]),
        color=CYAN,
        anim=FrameAnim(
          duration=20,
          delay=i * 10,
          frames=impact_frames
        )
      ) for i, cell in enumerate(target_cells)]

    def on_bump():
      delay = len(target_cells) * 10 + 10
      if target is None:
        game.anims[0].append(PauseAnim(
          duration=45 + delay,
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
              damage=16 + randint(-2, 2),
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
