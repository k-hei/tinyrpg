import gen
from anim import Anim
from stage import Stage
from log import Log

class Game:
  def __init__(game):
    game.reload()
    game.anims = []
    game.log = Log()

  def reload(game):
    game.stage = gen.dungeon(19, 19)
    game.p1 = next((actor for actor in game.stage.actors if actor.kind == "hero"), None)
    game.p2 = next((actor for actor in game.stage.actors if actor.kind == "mage"), None)

  def move(game, delta):
    source_cell = game.p1.cell
    (hero_x, hero_y) = source_cell
    (delta_x, delta_y) = delta
    target_cell = (hero_x + delta_x, hero_y + delta_y)
    target_tile = game.stage.get_tile_at(target_cell)
    target_actor = game.stage.get_actor_at(target_cell)
    if not target_tile.solid and (target_actor == None or target_actor == game.p2):
      game.anims.append(Anim(8, {
        "kind": "move",
        "actor": game.p1,
        "from": source_cell,
        "to": target_cell
      }))
      game.anims.append(Anim(8, {
        "kind": "move",
        "actor": game.p2,
        "from": game.p2.cell,
        "to": source_cell
      }))
      game.p2.cell = source_cell
      game.p1.cell = target_cell
      if target_tile is Stage.STAIRS:
        game.log.print("There's a staircase going up here.")
      return True
    else:
      if target_actor is not None:
        game.anims.append(Anim(10, {
          "kind": "flinch",
          "actor": target_actor
        }))
        if target_actor.kind == "eye":
          game.log.print("WARRIOR attacks")
          game.log.print("BEHOLDER receives 3 damage.")
        elif target_actor.kind == "chest":
          game.log.print("The lamp is sealed shut...")
        # game.stage.kill(target_actor)
      elif target_tile is Stage.DOOR:
        game.log.print("You open the door.")
        game.stage.set_tile_at(target_cell, Stage.DOOR_OPEN)
      game.anims.append(Anim(8, {
        "kind": "attack",
        "actor": game.p1,
        "from": source_cell,
        "to": target_cell
      }))
      return False

  def ascend(game):
    target_tile = game.stage.get_tile_at(game.p1.cell)
    if target_tile is Stage.STAIRS:
      game.reload()
      game.log.print("You go upstairs.")
      return True
    return False
