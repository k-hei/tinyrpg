from dungeon.actors import DungeonActor
from cores import Core
from assets import load as use_assets
from skills.ailment.virus import Virus
from skills.weapon.tackle import Tackle
from lib.cell import is_adjacent
import random

class Mushroom(DungeonActor):
  skill = Virus

  def __init__(mushroom):
    super().__init__(Core(
      name="Toadstool",
      faction="enemy",
      hp=27,
      st=14,
      en=8,
      skills=[ Tackle(), Virus() ]
    ))

  def step(actor, game):
    enemy = game.find_closest_enemy(actor)
    if enemy is None:
      return False

    if is_adjacent(actor.cell, enemy.cell):
      if random.randint(1, 5) == 1:
        game.use_skill(actor, Virus)
      else:
        game.attack(actor, enemy)
    else:
      game.move_to(actor, enemy.cell)

    return True

  def render(mushroom, anims):
    sprites = use_assets().sprites
    sprite = sprites["mushroom"]
    return super().render(sprite, anims)
