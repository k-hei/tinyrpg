from dungeon.actors import DungeonActor
from cores import Core
from assets import load as use_assets
from skills.attack.shieldbash import ShieldBash
from skills.weapon.club import Club
from lib.cell import is_adjacent
import random

class Skeleton(DungeonActor):
  skill = ShieldBash

  def __init__(skeleton):
    super().__init__(Core(
      name="Skeleton",
      faction="enemy",
      hp=35,
      st=14,
      en=9,
      skills=[ Club, ShieldBash ]
    ))

  def step(actor, game):
    enemy = game.find_closest_enemy(actor)
    if enemy is None:
      return False

    if is_adjacent(actor.cell, enemy.cell):
      if random.randint(1, 2) == 1:
        actor.face(enemy.cell)
        game.use_skill(actor, ShieldBash)
      else:
        game.attack(actor, enemy)
    else:
      game.move_to(actor, enemy.cell)

    return True

  def render(knight, anims):
    sprites = use_assets().sprites
    sprite = sprites["skeleton"]
    return super().render(sprite, anims)
