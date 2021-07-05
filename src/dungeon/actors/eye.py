from random import randint, choice
from lib.cell import is_adjacent
from config import ATTACK_DURATION
from dungeon.actors import DungeonActor
from cores import Core
from assets import load as use_assets
from skills.weapon.tackle import Tackle
from skills.ailment.steal import Steal
from anims.move import MoveAnim
from anims.attack import AttackAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from anims.awaken import AwakenAnim
from items.materials.angeltears import AngelTears
from sprite import Sprite
from filters import replace_color
from palette import BLACK, CYAN

class Eye(DungeonActor):
  drops = [AngelTears]

  def __init__(eye, faction="enemy", *args, **kwargs):
    super().__init__(Core(
      name="Eyeball",
      faction=faction,
      hp=20,
      st=12,
      en=7,
      skills=[ Tackle ],
      *args,
      **kwargs
    ))
    eye.item = None

  def step(eye, game):
    enemy = game.find_closest_enemy(eye)
    if enemy is None:
      return False

    if is_adjacent(eye.cell, enemy.cell):
      if not eye.item and eye.rare:
        game.use_skill(eye, Steal)
      else:
        game.attack(eye, enemy)
    else:
      game.move_to(eye, enemy.cell)

    return True

  def view(eye, anims):
    sprites = use_assets().sprites
    sprite = None
    for anim_group in anims:
      for anim in [a for a in anim_group if a.target is eye]:
        if type(anim) is AwakenAnim:
          return super().view(sprites["eye_attack"], anims)
    if eye.is_dead():
      return super().view(sprites["eye_flinch"], anims)
    anim_group = [a for a in anims[0] if a.target is eye] if anims else []
    for anim in anim_group:
      if type(anim) is MoveAnim:
        sprite = sprites["eye_attack"]
        break
      elif (type(anim) is AttackAnim
      and anim.time < anim.duration // 2):
        sprite = sprites["eye_attack"]
        break
      elif type(anim) in (FlinchAnim, FlickerAnim):
        sprite = sprites["eye_flinch"]
        break
    else:
      if eye.ailment == "sleep":
        sprite = sprites["eye_attack"]
      else:
        sprite = sprites["eye"]
    if eye.ailment == "freeze":
      sprite = sprites["eye_flinch"]
    return super().view(sprite, anims)
