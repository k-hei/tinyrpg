import gen
from anim import Anim
from stage import Stage

class Game:
  def __init__(game):
    game.stage = gen.dungeon(19, 19)
    game.p1 = next((actor for actor in game.stage.actors if actor.kind == "hero"), None)
    game.p2 = next((actor for actor in game.stage.actors if actor.kind == "mage"), None)
    game.anims = []

  def move(game, delta):
    source_cell = game.p1.cell
    (hero_x, hero_y) = source_cell
    (delta_x, delta_y) = delta
    target_cell = (hero_x + delta_x, hero_y + delta_y)
    target_tile = game.stage.get_at(target_cell)
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
      return True
    else:
      if target_actor is not None:
        game.stage.kill(target_actor)
      if target_tile is Stage.DOOR:
        game.stage.set_at(target_cell, Stage.DOOR_OPEN)
      game.anims.append(Anim(6, {
        "kind": "attack",
        "actor": game.p1,
        "from": source_cell,
        "to": target_cell
      }))
      return False
