from dungeon.actors import DungeonActor
from cores import Core, Stats
from assets import load as use_assets
from skills.attack.cleave import Cleave
from skills.weapon.club import Club
from lib.cell import is_adjacent
import random
from sprite import Sprite

class Mummy(DungeonActor):
  skill = Cleave

  def __init__(soldier):
    super().__init__(Core(
      name="Mummy",
      faction="enemy",
      stats=Stats(
        hp=8,
        st=12,
        dx=3,
        ag=5,
        lu=3,
        en=14,
      ),
      skills=[ Club, Cleave ]
    ))

  def step(soldier, game):
    enemy = game.find_closest_enemy(soldier)
    if enemy is None:
      return False

    if is_adjacent(soldier.cell, enemy.cell):
      if random.randint(1, 3) == 1:
        soldier.face(enemy.cell)
        game.use_skill(soldier, Cleave)
      else:
        game.attack(soldier, enemy)
    else:
      game.move_to(soldier, enemy.cell)

    return True

  def view(soldier, anims):
    sprites = use_assets().sprites
    sprite = sprites["soldier"]
    return super().view(sprite, anims)
