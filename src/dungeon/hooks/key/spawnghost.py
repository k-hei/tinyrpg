import lib.vector as vector
from dungeon.actors.ghost import Ghost
from anims.warpin import WarpInAnim

def spawn_ghost(room, game, on_end=None):
  ghost = Ghost()
  ghost_cell = vector.add(room.get_doors(game.stage)[0].cell, (0, -1))
  game.stage.spawn_elem_at(ghost_cell, ghost)
  game.anims.append([WarpInAnim(target=ghost, on_end=on_end)])
