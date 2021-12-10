from random import randint
from lib.cell import is_adjacent, manhattan
from dungeon.actors import DungeonActor
from cores import Core, Stats
from skills.ailment.virus import Virus
from skills.weapon.tackle import Tackle
from items.materials.redferrule import RedFerrule
import assets
from lib.sprite import Sprite
import tiles.default as tileset

from anims.step import StepAnim
from anims.attack import AttackAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from anims.shake import ShakeAnim
from anims.bounce import BounceAnim
from config import PUSH_DURATION

class Mushroom(DungeonActor):
  skill = Virus
  drops = [RedFerrule]
  COOLDOWN_DURATION = 6

  class ChargeAnim(ShakeAnim): pass

  def __init__(mushroom, name="Toadstool", *args, **kwargs):
    super().__init__(Core(
      name=name,
      faction="enemy",
      stats=Stats(
        hp=19,
        st=14,
        dx=4,
        ag=4,
        en=10,
      ),
      skills=[Tackle, Virus],
      message=[(name, "Ahn<3 I'm cooominggggg!!")]
    ), *args, **kwargs)
    mushroom.damaged = False

  def damage(mushroom, *args, **kwargs):
    super().damage(*args, **kwargs)
    mushroom.damaged = True

  def charge(mushroom, *args, **kwargs):
    super().charge(*args, **kwargs)
    mushroom.core.anims.append(Mushroom.ChargeAnim())

  def kill(mushroom, game=None, *args, **kwargs):
    super().kill(game=game, *args, **kwargs)
    if mushroom.charge_skill and game and not issubclass(game.stage.get_tile_at(mushroom.cell), tileset.Pit):
      Virus.effect(user=mushroom, dest=None, game=game)

  def step(mushroom, game):
    enemy = game.find_closest_enemy(mushroom)
    if not mushroom.aggro:
      return super().step(game)
    if not enemy:
      return None

    can_charge = not mushroom.charge_cooldown and (randint(1, 3) == 1 or mushroom.damaged)
    if mushroom.damaged:
      mushroom.damaged = False
    if can_charge and manhattan(mushroom.cell, enemy.cell) <= 2:
      return mushroom.charge(skill=Virus, dest=game.hero.cell)
    elif is_adjacent(mushroom.cell, enemy.cell):
      return ("attack", enemy)
    else:
      return ("move_to", enemy.cell)

  def view(mushroom, anims):
    mushroom_image = None
    offset_x, offset_y = 0, 0
    if mushroom.is_dead():
      return super().view(assets.sprites["mushroom_flinch"], anims)
    anim_group = [a for a in anims[0] if a.target is mushroom] if anims else []
    anim_group += mushroom.core.anims
    for anim in anim_group:
      if type(anim) is StepAnim and anim.duration != PUSH_DURATION:
        mushroom_image = assets.sprites["mushroom_move"]
        break
      elif (type(anim) is AttackAnim
      and anim.time < anim.duration // 2):
        mushroom_image = assets.sprites["mushroom_move"]
        break
      elif type(anim) in (FlinchAnim, FlickerAnim):
        mushroom_image = assets.sprites["mushroom_flinch"]
        break
      elif type(anim) is Mushroom.ChargeAnim:
        mushroom_image = assets.sprites["mushroom_move"]
        offset_x += anim.offset
        break
      elif type(anim) is BounceAnim:
        mushroom_image = assets.sprites["mushroom_move"]
        break
    else:
      if mushroom.ailment == "sleep" or mushroom.get_hp() < mushroom.get_hp_max() / 2:
        mushroom_image = assets.sprites["mushroom_sleep"]
      else:
        mushroom_image = assets.sprites["mushroom"]
    if mushroom.ailment == "freeze":
      mushroom_image = assets.sprites["mushroom_flinch"]
    return super().view([Sprite(
      image=mushroom_image,
      pos=(offset_x, offset_y)
    )], anims)
