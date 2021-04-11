import gen
from anim import Anim
from stage import Stage
from log import Log

class Game:
  MOVE_DURATION = 8
  FLINCH_DURATION = 10
  ATTACK_DURATION = 8

  def __init__(game):
    game.reload()
    game.anims = []
    game.log = Log()

  def reload(game, swapped=False):
    game.stage = gen.dungeon(19, 19)
    game.p1 = next((actor for actor in game.stage.actors if actor.kind == "hero"), None)
    game.p2 = next((actor for actor in game.stage.actors if actor.kind == "mage"), None)
    if swapped:
      game.swap()

  def move(game, delta):
    source_cell = game.p1.cell
    (hero_x, hero_y) = source_cell
    (delta_x, delta_y) = delta
    game.p1.facing = delta
    target_cell = (hero_x + delta_x, hero_y + delta_y)
    target_tile = game.stage.get_tile_at(target_cell)
    target_actor = game.stage.get_actor_at(target_cell)
    if not target_tile.solid and (target_actor is None or target_actor is game.p2):
      game.anims.append(Anim(Game.MOVE_DURATION, {
        "kind": "move",
        "actor": game.p1,
        "from": source_cell,
        "to": target_cell
      }))
      game.anims.append(Anim(Game.MOVE_DURATION, {
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
        game.anims.append(Anim(Game.FLINCH_DURATION, {
          "kind": "flinch",
          "actor": target_actor
        }))
        if target_actor.kind == "eye":
          game.log.print("WARRIOR attacks")
          game.log.print("EYEBALL receives 3 damage.")
        elif target_actor.kind == "chest":
          game.log.print("The lamp is sealed shut...")
        # game.stage.kill(target_actor)
      elif target_tile is Stage.DOOR:
        game.log.print("You open the door.")
        game.stage.set_tile_at(target_cell, Stage.DOOR_OPEN)
      game.anims.append(Anim(Game.ATTACK_DURATION, {
        "kind": "attack",
        "actor": game.p1,
        "from": source_cell,
        "to": target_cell
      }))
      return False

  def swap(game):
    game.p1, game.p2 = (game.p2, game.p1)

  def special(game):
    if game.p1.kind == "hero":
      game.shield_bash()
    elif game.p1.kind == "mage":
      game.detect_mana()

  def detect_mana(game):
    game.log.print("MAGE uses Detect Mana")
    game.log.print("There's nothing magical nearby.")

  def shield_bash(game):
    source_cell = game.p1.cell
    hero_x, hero_y = source_cell
    delta_x, delta_y = game.p1.facing
    target_cell = (hero_x + delta_x, hero_y + delta_y)
    target_actor = game.stage.get_actor_at(target_cell)
    game.anims.append(Anim(Game.ATTACK_DURATION, {
      "kind": "attack",
      "actor": game.p1,
      "from": source_cell,
      "to": target_cell
    }))
    game.log.print("WARRIOR uses Shield Bash")

    if target_actor is not None and target_actor is not game.p2:
      # nudge target actor 1 square in the given direction
      target_x, target_y = target_cell
      nudge_cell = (target_x + delta_x, target_y + delta_y)
      nudge_tile = game.stage.get_tile_at(nudge_cell)
      nudge_actor = game.stage.get_actor_at(nudge_cell)
      game.anims.append(Anim(Game.FLINCH_DURATION, {
        "kind": "flinch",
        "actor": target_actor
      }))
      if not nudge_tile.solid and nudge_actor is None:
        target_actor.cell = nudge_cell
        game.anims.append(Anim(Game.MOVE_DURATION, {
          "kind": "move",
          "actor": target_actor,
          "from": target_cell,
          "to": nudge_cell
        }))
        if target_actor.kind == "eye":
          game.log.print("EYEBALL is reeling.")
    else:
      game.log.print("But nothing happened...")

  def ascend(game):
    target_tile = game.stage.get_tile_at(game.p1.cell)
    if target_tile is Stage.STAIRS:
      swapped = game.p1.kind == "mage"
      game.reload(swapped)
      game.log.print("You go upstairs.")
      return True
    return False
