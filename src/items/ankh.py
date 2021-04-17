from assets import load as use_assets

class Ankh:
  def __init__(ankh):
    ankh.name = "Ankh"
    ankh.desc = "Revives the dead with half HP"

  def effect(ankh, game):
    hero = game.hero
    ally = game.ally
    floor = game.floor
    if not ally.dead:
      return (False, "Your partner is still alive!")

    col, row = hero.cell
    neighbors = [
      (col - 1, row),
      (col + 1, row),
      (col, row - 1),
      (col, row + 1)
    ]
    neighbor = next((n for n in neighbors if floor.is_cell_empty(n)), None)
    if neighbor is None:
      return (False, "There's nowhere for " + ally.name.upper() + " to spawn...")

    ally.hp = ally.hp_max // 2
    ally.dead = False
    floor.spawn_actor(ally, neighbor)
    return (True, ally.name.upper() + " was revived.")

  def render(ankh):
    return use_assets().sprites["icon_ankh"]
