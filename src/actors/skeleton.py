from assets import load as use_assets
from actors import Actor
from skills.shieldbash import ShieldBash
from cell import is_adjacent
import random

class Skeleton(Actor):
  def __init__(skeleton):
    super().__init__(
      name="Skeleton",
      faction="enemy",
      hp=35,
      st=16,
      en=9,
      skills=[ShieldBash]
    )

  def step(actor, game):
    enemy = game.find_closest_enemy(actor)
    if enemy is None:
      return False

    if is_adjacent(actor.cell, enemy.cell):
      if random.randint(1, 2) == 1:
        actor.face(enemy.cell)
        game.use_skill(actor, ShieldBash)
      else:
        game.log.print(actor.name.upper() + " attacks")
        game.attack(actor, enemy)
    else:
      game.move_to(actor, enemy.cell)

    return True

  def render(knight, anims):
    sprites = use_assets().sprites
    sprite = sprites["skeleton"]
    return super().render(sprite, anims)
