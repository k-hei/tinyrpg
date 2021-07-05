from skills.attack import AttackSkill
from config import ATTACK_DURATION, TILE_SIZE
from anims.attack import AttackAnim
from anims.pause import PauseAnim
from anims.attack import AttackAnim
from anims.frame import FrameAnim
from dungeon.actors import DungeonActor
from cores.knight import Knight as Knight
from skills import find_skill_targets
from vfx import Vfx
from random import randint

class RendingGale(AttackSkill):
  name = "RendingGale"
  desc = "Slashes a row"
  element = "sword"
  cost = 5
  range_type = "row"
  range_min = 1
  range_max = 2
  range_radius = 0
  users = [Knight]
  blocks = (
    (0, 0),
    (1, 0),
    (2, 0),
  )

  def effect(user, dest, game, on_end=None):
    camera = game.camera
    floor = game.floor
    hero_x, hero_y = user.cell
    facing_x, facing_y = user.facing
    target_cells = find_skill_targets(RendingGale, user)
    target_cell = (hero_x + facing_x, hero_y + facing_y)
    targets = [e for e in [floor.get_elem_at(c, superclass=DungeonActor) for c in target_cells] if e]

    def connect():
      impact_frames = ["fx_impact{}".format(i) for i in range(7)]
      game.vfx += [Vfx(
        kind="impact",
        pos=tuple([x * TILE_SIZE for x in cell]),
        anim=FrameAnim(
          duration=20,
          delay=i * 10,
          frames=impact_frames
        )
      ) for i, cell in enumerate(target_cells)]

    def find_damage(target):
      en = target.core.en if not target.ailment == "sleep" else 0
      return int((user.core.st + user.weapon.st) * 1.25 - en) + randint(-2, 2)

    def next_target():
      if not targets:
        return on_end and on_end()
      target = targets.pop(0)
      game.flinch(
        target=target,
        damage=find_damage(target),
        on_end=next_target
      )

    def end_bump():
      if not targets:
        return game.anims[0].append(PauseAnim(
          duration=45,
          on_end=lambda: (
            game.log.print("But nothing happened..."),
            on_end and on_end()
          )
        ))
      game.anims[0].append(PauseAnim(
        duration=45,
        on_end=next_target
      ))

    game.anims.append([AttackAnim(
      duration=ATTACK_DURATION,
      target=user,
      src=user.cell,
      dest=target_cell,
      on_connect=connect,
      on_end=end_bump
    )])

    return target_cell
