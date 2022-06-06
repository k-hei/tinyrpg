import lib.vector as vector
from lib.cell import manhattan
from dungeon.actors.ghost import Ghost
from anims.warpin import WarpInAnim

def spawn_ghost(room, game, on_end=None):
  neighbor_room = (room
    if len(game.stage.rooms) == 1
    else sorted(game.stage.rooms, key=lambda r: manhattan(r.origin, room.origin))[0])

  doors = neighbor_room.get_doors(game.stage)
  door = sorted(doors, key=lambda d: d.cell[1])[-1] if doors else None
  if not door:
    on_end()

  door_cell = door.cell
  ghost = Ghost(aggro=1)
  ghost_cell = vector.add(door_cell, (0, -1))
  game.stage.spawn_elem_at(ghost_cell, ghost)
  game.anims.append([WarpInAnim(target=ghost, on_end=on_end)])
