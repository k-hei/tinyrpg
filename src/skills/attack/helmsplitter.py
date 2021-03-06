from skills import Skill
from anims.attack import AttackAnim
from anims.pause import PauseAnim
from anims.attack import AttackAnim
from dungeon.actors.knight import Knight
from config import ATTACK_DURATION

class HelmSplitter(Skill):
  name = "HelmSplitter"
  element = "axe"
  desc = "Stuns target with mighty swing"
  cost = 6
  users = (Knight,)

  def effect(user, game, on_end=None):
    camera = game.camera
    floor = game.stage
    hero_x, hero_y = user.cell
    delta_x, delta_y = user.facing
    target_cell = (hero_x + delta_x, hero_y + delta_y)
    target_elem = floor.get_elem_at(target_cell)
    camera.focus(target_cell)
    game.anims.append([
      AttackAnim(
        duration=ATTACK_DURATION,
        target=user,
        src=user.cell,
        dest=target_cell,
        on_end=lambda: (game.anims[0].append(PauseAnim(
          duration=45,
          on_end=lambda: (
            game.log.print("But nothing happened..."),
            camera.blur(),
            on_end()
          )
        )))
      )
    ])
