import lib.vector as vector
from dungeon.actors.ghost import Ghost
from anims.warpin import WarpInAnim

def spawn_ghost(room, game, on_end=None):
  doors = room.get_doors(game.stage)
  door = doors[0] if doors else None
  if not door:
    on_end()

  door_cell = door.cell
  ghost = Ghost()
  ghost_cell = vector.add(door_cell, (0, -1))
  game.stage.spawn_elem_at(ghost_cell, ghost)
  game.anims.append([WarpInAnim(target=ghost, on_end=on_end)])
