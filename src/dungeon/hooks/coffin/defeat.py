from dungeon.props.coffin import Coffin

def on_defeat(room, game, actor):
  if [e for e in room.get_enemies(game.floor) if e is not actor] or actor.faction != "enemy":
    return True

  for cell in room.cells:
    for elem in game.floor.get_elems_at(cell):
      if type(elem) is Coffin:
        elem.unlock()

  for door in room.get_doors(game.floor):
    door.handle_open(game)
    door.locked = False

  return True
