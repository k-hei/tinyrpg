from random import randint
from skills.attack import AttackSkill
from anims.attack import AttackAnim
from anims.pause import PauseAnim
from anims.frame import FrameAnim
from dungeon.actors import DungeonActor
from cores.knight import Knight as Knight
from vfx import Vfx
from config import TILE_SIZE

class Cleave(AttackSkill):
  name = "Cleave"
  desc = "Slash with increased power"
  element = "sword"
  cost = 3
  users = [Knight]
  blocks = (
    (1, 0),
    (0, 1),
    (1, 1)
  )

  def effect(user, dest, game, on_end=None):
    floor = game.floor
    hero_x, hero_y = user.cell
    delta_x, delta_y = user.facing
    target_cell = (hero_x + delta_x, hero_y + delta_y)
    target_elem = floor.get_elem_at(target_cell, superclass=DungeonActor)

    def on_connect():
      game.vfx.append(Vfx(
        kind="impact",
        pos=tuple([x * TILE_SIZE for x in target_cell]),
        anim=FrameAnim(
          duration=20,
          frames=["fx_impact{}".format(i) for i in range(7)]
        )
      ))

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
            game.log.print("But nothing happened..."),
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
