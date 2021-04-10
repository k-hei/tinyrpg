import gen
from anim import Anim

class Game:
  def __init__(game):
    game.stage = gen.maze(19, 19)
    game.p1 = next((actor for actor in game.stage.actors if actor.kind == "hero"), None)
    game.p2 = next((actor for actor in game.stage.actors if actor.kind == "mage"), None)
    game.anims = []
  def move(game, delta):
    old_cell = game.p1.cell
    (hero_x, hero_y) = old_cell
    (delta_x, delta_y) = delta
    new_cell = (hero_x + delta_x, hero_y + delta_y)
    target_tile = game.stage.get_at(new_cell)
    target_actor = game.stage.get_actor_at(new_cell)
    if target_tile != 1 and (target_actor == None or target_actor == game.p2):
      game.anims.append(Anim(6, {
        "target": game.p1,
        "from": old_cell,
        "to": new_cell
      }))
      game.anims.append(Anim(6, {
        "target": game.p2,
        "from": game.p2.cell,
        "to": old_cell
      }))
      game.p2.cell = old_cell
      game.p1.cell = new_cell
      return True
    elif target_actor is not None:
      game.stage.kill(target_actor)
      return False
    else:
      return False
