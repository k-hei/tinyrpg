from skills.attack import AttackSkill
from dungeon.actors import DungeonActor
from cores.knight import Knight
from anims.attack import AttackAnim
from anims.pause import PauseAnim
from helpers.combat import find_damage

class ShieldBash(AttackSkill):
  name = "ShieldBash"
  desc = "Pushes target one square"
  element = "shield"
  cost = 2
  users = [Knight]
  blocks = (
    (0, 0),
    (1, 0),
    (1, 1),
    (1, 2),
  )

  def effect(game, user, dest, on_start=None, on_end=None):
    source_cell = user.cell
    hero_x, hero_y = source_cell
    delta_x, delta_y = user.facing
    target_cell = (hero_x + delta_x, hero_y + delta_y)
    target_elem = next((e for e in game.stage.get_elems_at(target_cell) if isinstance(e, DungeonActor)), None)

    if target_elem is None:
      game.anims.append([
        AttackAnim(
          target=user,
          src=user.cell,
          dest=target_cell,
          on_start=on_start,
          on_end=lambda: game.anims[0].append(PauseAnim(
            duration=45,
            on_end=on_end
          ))
        )
      ])
    else:
      game.anims.append([
        AttackAnim(
          target=user,
          src=user.cell,
          dest=target_cell,
          on_start=on_start,
          on_connect=lambda: (
            game.flinch(
              target=target_elem,
              damage=find_damage(user, target_elem, modifier=0.8),
              direction=user.facing,
              on_end=on_end,
            ),
            game.nudge(actor=target_elem, direction=user.facing),
          )
        )
      ])
