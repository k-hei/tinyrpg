from dungeon.actors import DungeonActor
from cores import Core, Stats
from assets import load as use_assets
from skills.attack.shieldbash import ShieldBash
from skills.weapon.club import Club
from lib.cell import is_adjacent
import random
from lib.sprite import Sprite

class Skeleton(DungeonActor):
  skill = ShieldBash
  drops = [Club]

  def __init__(skeleton, rare=False, *args, **kwargs):
    super().__init__(Core(
      name="Skeleton",
      faction="enemy",
      stats=Stats(
        hp=23,
        st=16,
        dx=7,
        ag=5,
        en=12,
      ),
      skills=[ Club, ShieldBash ]
    ), *args, **kwargs)
    if rare:
      skeleton.promote()

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

  def view(skeleton, anims):
    sprites = use_assets().sprites
    sprite = sprites["skeleton"]
    return super().view(sprite, anims)
