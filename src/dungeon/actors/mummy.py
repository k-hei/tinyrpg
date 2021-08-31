from random import randint
from dungeon.actors import DungeonActor
from cores import Core, Stats
from skills.attack.cleave import Cleave
from skills.weapon.club import Club
from lib.cell import is_adjacent
from sprite import Sprite
import assets
from anims.move import MoveAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from config import PUSH_DURATION
from items.materials.crownjewel import CrownJewel

class Mummy(DungeonActor):
  skill = Cleave
  drops = [CrownJewel]

  def __init__(soldier):
    super().__init__(Core(
      name="Mummy",
      faction="enemy",
      stats=Stats(
        hp=8,
        st=12,
        dx=3,
        ag=4,
        lu=3,
        en=13,
      ),
      skills=[ Club, Cleave ]
    ))

  def step(soldier, game):
    enemy = game.find_closest_enemy(soldier)
    if enemy is None:
      return False

    if is_adjacent(soldier.cell, enemy.cell):
      if randint(1, 3) == 1:
        soldier.face(enemy.cell)
        game.use_skill(soldier, Cleave)
      else:
        game.attack(soldier, enemy)
    else:
      game.move_to(soldier, enemy.cell)

    return True

  def view(soldier, anims):
    sprite = assets.sprites["soldier"]
    anim_group = [a for a in anims[0] if a.target is soldier] if anims else []
    for anim in anim_group:
      if type(anim) is MoveAnim and anim.duration != PUSH_DURATION:
        sprite = assets.sprites["soldier_move"]
        break
      elif type(anim) in (FlinchAnim, FlickerAnim):
        sprite = assets.sprites["soldier_flinch"]
        break
    else:
      if soldier.ailment == "sleep":
        sprite = assets.sprites["soldier_sleep"]
      else:
        sprite = assets.sprites["soldier"]
    if soldier.ailment == "freeze":
      sprite = assets.sprites["soldier_flinch"]
    return super().view(sprite, anims)
