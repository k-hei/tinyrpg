def on_defeat(room, game, actor):
  enemies = [e for e in room.get_enemies(game.floor) if e is not actor]
  if actor.faction != "enemy" or game.room is not room:
    return True
  if not enemies:
    room.unlock(game)
  return True
