from skills.attack import AttackSkill
from dungeon.actors import DungeonActor
from cores.knight import Knight as Knight
from vfx.claw import ClawVfx
from lib.cell import add as add_vector
from anims.step import StepAnim
from anims.attack import AttackAnim

class ClawRush(AttackSkill):
  name = "ClawRush"
  desc = "Lunges at foe with deadly slash"
  element = "fist"
  cost = 3
  range_type = "linear"
  range_min = 1
  range_max = 2
  range_radius = 0
  users = [Knight]
  blocks = (
    (0, 0),
    (1, 0),
    (2, 0),
    (2, 1)
  )
  charge_turns = 1

  def effect(user, dest, game, on_end=None):
    origin_cell = user.cell
    dest_cell = add_vector(origin_cell, user.facing)
    if game.stage.is_cell_empty(dest_cell):
      target_cell = add_vector(dest_cell, user.facing)
    else:
      target_cell = dest_cell
      dest_cell = origin_cell

    target_elems = game.stage.get_elems_at(target_cell)
    target_elem = next((e for e in target_elems if e.breakable), None)
    target_actor = next((e for e in target_elems if isinstance(e, DungeonActor)), None)
    print("elem", target_elem, "actor", target_actor)
    def attack():
      not game.anims and game.anims.append([])
      game.anims[0].append(AttackAnim(
        target=user,
        src=dest_cell,
        dest=target_cell,
        on_start=lambda: game.vfx.append(ClawVfx(cell=target_cell)),
        on_connect=(lambda: game.attack(
          actor=user,
          target=target_actor,
          modifier=1.5,
          animate=False
        )) if target_actor else (lambda: (
          target_elem.crush(game)
        )) if target_elem else None,
        on_end=on_end
      ))
    if dest_cell == origin_cell:
      attack()
    else:
      game.anims.append([
        StepAnim(
          target=user,
          src=origin_cell,
          dest=dest_cell,
          duration=10,
          on_end=lambda: (
            setattr(user, "cell", dest_cell),
            attack()
          )
        )
      ])
    return False
