from math import pi, inf
from random import choice, shuffle
from helpers.stage import is_cell_walkable_to_actor
import lib.vector as vector
from lib.cell import downscale, neighborhood
from skills.magic import MagicSkill
from anims.pause import PauseAnim
from cores.mage import Mage
from dungeon.actors.mage import LeapAnim
from dungeon.actors.mageclone import MageClone
from vfx.mageclone import MageCloneVfx


class Roulette(MagicSkill):
  name = "Illusion"
  desc = "Calls allies to your side"
  element = "shield"
  cost = 12
  range_min = 1
  range_max = 2
  range_type = "radial"
  charge_turns = 1
  users = [Mage]
  blocks = (
    (0, 0),
    (0, 1),
    (1, 0),
    (1, 1),
  )

  def effect(game, user, dest=None, on_start=None, on_end=None):
    NUM_CLONES = 4
    on_start and on_start(user.cell)
    game.darken()

    def jump(fx):
      start_cell = user.cell
      pause_anim.end()
      game.anims.extend([
        [LeapAnim(
          target=user,
          src=user.cell,
          dest=vector.add(user.cell, (-1, -1)),
          height=36,
          duration=45,
          on_end=lambda: (
            setattr(user, "hidden", True),
            user_clone := MageCloneVfx(
              cell=start_cell,
              color=user.color(),
              angle=fx.angle + 2 * pi * 1 / 5,
              animated=False,
            ),
            game.vfx.append(user_clone),
            shuffle(game.vfx),
            game.anims.extend([
              [PauseAnim(duration=30)],
              *[(lambda f: [
                pause_anim := PauseAnim(
                  duration=15,
                  on_end=lambda: (
                    clone_cell := choice([c for c in neighborhood(start_cell, radius=3)
                      if is_cell_walkable_to_actor(game.stage, c, user)
                      and c in game.room.cells] or game.room.cells),
                    clone := (user
                      if f is user_clone
                      else MageClone(aggro=2, faction=user.faction)),
                    (
                      setattr(user, "hidden", False),
                      user.core.anims.pop(),
                    ) if f is user_clone else game.stage.spawn_elem_at(
                      cell=clone_cell,
                      elem=clone,
                    ),
                    f in game.vfx and game.vfx.remove(f),
                    anim_group := next((g for g in game.anims if pause_anim in g), None),
                    anim_group.append(LeapAnim(
                      target=clone,
                      src=vector.add(downscale(f.pos, game.stage.tile_size), (0, -0.5)),
                      dest=clone_cell,
                      height=64,
                      duration=45,
                    )),
                  )
                )
              ])(f) for f in game.vfx if type(f) is MageCloneVfx],
              [PauseAnim(duration=30, on_end=lambda: (
                game.undarken(),
                on_end and on_end(),
              ))]
            ])
          )
        )],
      ])

    clones = [
      MageCloneVfx(cell=user.cell, color=user.color(), angle=2 * pi * 0 / 4),
      MageCloneVfx(cell=user.cell, color=user.color(), angle=2 * pi * 1 / 4),
      MageCloneVfx(cell=user.cell, color=user.color(), angle=2 * pi * 2 / 4),
      MageCloneVfx(cell=user.cell, color=user.color(), angle=2 * pi * 3 / 4, on_ready=jump),
    ]
    shuffle(clones)
    game.vfx.extend(clones)

    game.anims.append([pause_anim := PauseAnim(duration=inf)])
    return False
