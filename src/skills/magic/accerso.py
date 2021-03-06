from random import choice
from skills.magic import MagicSkill
from anims.pause import PauseAnim
from anims.bounce import BounceAnim
from anims.warpin import WarpInAnim
from cores.mage import Mage
from dungeon.actors.eyeball import Eyeball
from config import ENABLED_COMBAT_LOG
import locations.default.tileset as tileset

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

  def effect(game, user, dest, on_start=None, on_end=None):
    floor = game.stage
    valid_cells = [c for c in Accerso().find_range(user, floor) if floor.is_cell_empty(c) and issubclass(floor.get_tile_at(c), tileset.Floor)]
    target_count = 2
    target_cells = []
    while valid_cells and len(target_cells) < target_count:
      cell = choice(valid_cells)
      valid_cells.remove(cell)
      target_cells.append(cell)

    def on_bounce():
      if target_cells:
        for i, cell in enumerate(target_cells):
          ally = Eyeball(
            faction="enemy" if user.faction == "enemy" else "ally",
            aggro=3
          )
          # ally.command = True
          floor.spawn_elem_at(cell, ally)
          game.anims[0].append(WarpInAnim(
            target=ally,
            duration=15,
            delay=i * 10,
            on_end=(on_end if cell == target_cells[-1] else lambda: None)
          ))
        if ENABLED_COMBAT_LOG:
          if user.faction == "player":
            game.log.print("Allies have appeared!")
          elif user.faction == "enemy":
            game.log.print("Enemies have appeared!")
      else:
        if ENABLED_COMBAT_LOG:
          game.log.print("But nothing happened...")
        on_end and on_end()

    game.anims.append([BounceAnim(
      duration=20,
      target=user,
      on_start=on_start,
      on_end=lambda: game.anims[0].append(PauseAnim(
        duration=15,
        on_end=on_bounce
      ))
    )])

    return dest
