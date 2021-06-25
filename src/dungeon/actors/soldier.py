from dungeon.actors import DungeonActor
from cores import Core
from assets import load as use_assets
from skills.attack.blitzritter import Blitzritter
from skills.weapon.club import Club
from lib.cell import is_adjacent
import random
from sprite import Sprite

class Soldier(DungeonActor):
  skill = Blitzritter

  def __init__(soldier):
    super().__init__(Core(
      name="Soldier",
      faction="enemy",
      hp=32,
      st=15,
      en=11,
      skills=[ Club, Blitzritter ]
    ))

  def step(soldier, game):
    enemy = game.find_closest_enemy(soldier)
    if enemy is None:
      return False

    if is_adjacent(soldier.cell, enemy.cell):
      if random.randint(1, 3) == 1:
        soldier.face(enemy.cell)
        game.use_skill(soldier, Blitzritter)
      else:
        game.attack(soldier, enemy)
    else:
      game.move_to(soldier, enemy.cell)

    return True

  def view(soldier, anims):
    sprites = use_assets().sprites
    sprite = sprites["soldier"]
    return super().view(sprite, anims)
