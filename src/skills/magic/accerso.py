from random import randint, choice
from skills import find_skill_targets
from skills.magic import MagicSkill
from anims.pause import PauseAnim
from anims.bounce import BounceAnim
from anims.warpin import WarpInAnim
from cores.mage import Mage
from dungeon.actors.eye import Eye

class Accerso(MagicSkill):
  name = "Accerso"
  desc = "Calls allies to your side"
  element = "shield"
  cost = 12
  range_min = 1
  range_max = 2
  range_type = "radial"
  users = [Mage]
  blocks = (
    (0, 0),
    (0, 1),
    (1, 0),
    (1, 1),
  )

  def effect(user, dest, game, on_end=None):
    floor = game.floor
    valid_cells = [c for c in find_skill_targets(Accerso, user, floor) if floor.is_cell_empty(c)]
    target_count = randint(2, 3)
    target_cells = []
    while valid_cells and len(target_cells) < target_count:
      cell = choice(valid_cells)
      valid_cells.remove(cell)
      target_cells.append(cell)

    def on_bounce():
      if target_cells:
        for i, cell in enumerate(target_cells):
          ally = Eye(faction="ally" if user.get_faction() == "player" else "enemy")
          ally.stepped = True
          floor.spawn_elem_at(cell, ally)
          game.anims[0].append(WarpInAnim(
            target=ally,
            duration=15,
            delay=i * 10
          ))
        game.log.print("Allies have appeared!")
        on_end and on_end()
      else:
        game.log.print("But nothing happened...")
        on_end and on_end()

    game.anims.append([BounceAnim(
      duration=20,
      target=user,
      on_end=lambda: game.anims[0].append(PauseAnim(
        duration=15,
        on_end=on_bounce
      ))
    )])

    return dest
