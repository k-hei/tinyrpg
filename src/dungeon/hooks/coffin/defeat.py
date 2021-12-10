from dungeon.props.coffin import Coffin

def on_defeat(room, game, actor):
  if [e for e in room.get_enemies(game.stage) if e is not actor] or actor.faction != "enemy":
    return True

  for cell in room.cells:
    for elem in game.stage.get_elems_at(cell):
      if type(elem) is Coffin:
        elem.unlock()

  for door in room.get_doors(game.stage):
    door.handle_open(game)
    door.locked = False

  return True
