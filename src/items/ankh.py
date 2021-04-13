from assets import load as use_assets

class Ankh:
  def __init__(ankh):
    ankh.name = "Ankh"
    ankh.description = "Revives the dead with half HP"

  def effect(ankh, game):
    hero = game.hero
    ally = game.ally
    floor = game.floor
    if ally.dead:
      col, row = hero.cell
      neighbors = [
        (col - 1, row),
        (col + 1, row),
        (col, row - 1),
        (col, row + 1)
      ]
      for neighbor in neighbors:
        if not floor.get_tile_at(neighbor).solid and floor.get_actor_at(neighbor) is None:
          ally.hp = ally.hp_max // 2
          ally.dead = False
          floor.spawn_actor(ally, neighbor)
          return (True, ally.name.upper() + " was revived.")
          break
      else:
        return (False, "There's nowhere for " + ally.name.upper() + " to spawn...")
    else:
      return (False, "Your partner is still alive!")

  def render(ankh):
    assets = use_assets()
    return assets.sprites["icon_ankh"]
