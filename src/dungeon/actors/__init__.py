import random
from dungeon.element import DungeonElement
from cores import Core
from skills.weapon import Weapon

import palette
from assets import load as use_assets
from filters import replace_color, darken
from anims.awaken import AwakenAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from lib.cell import is_adjacent, manhattan
from comps.log import Token

class DungeonActor(DungeonElement):
  POISON_DURATION = 5
  POISON_STRENGTH = 1 / 6
  skill = None

  def __init__(actor, core):
    super().__init__(solid=True)
    actor.core = core
    actor.weapon = actor.load_weapon()
    actor.solid = True
    actor.stepped = False
    actor.ailment = None
    actor.ailment_turns = 0
    actor.counter = False
    actor.aggro = False
    actor.idle = False
    actor.rare = False
    actor.facing = (1, 0)
    actor.visible_cells = []

  def get_name(actor): return actor.core.name
  def get_faction(actor): return actor.core.faction
  def get_hp(actor): return actor.core.get_hp()
  def get_hp_max(actor): return actor.core.get_hp_max()
  def set_hp(actor, hp): actor.core.set_hp(hp)
  def get_skills(actor): return actor.core.skills
  def get_active_skills(actor): return actor.core.get_active_skills()
  def is_dead(actor): return actor.core.dead

  def load_weapon(actor):
    return next((s for s in actor.core.skills if s.kind == "weapon"), None)

  def allied(actor, target):
    if target is None or not isinstance(target, DungeonActor):
      return False
    else:
      return Core.allied(actor.core, target.core)

  def face(actor, dest):
    actor_x, actor_y = actor.cell
    dest_x, dest_y = dest
    delta_x = dest_x - actor_x
    delta_y = dest_y - actor_y
    if abs(delta_x) >= abs(delta_y):
      actor.facing = int(delta_x / (abs(delta_x) or 1)), 0
    else:
      actor.facing = 0, int(delta_y / (abs(delta_y) or 1))

  def inflict_ailment(actor, ailment):
    if ailment == actor.ailment:
      return False
    if ailment == "poison":
      actor.ailment_turns = DungeonActor.POISON_DURATION
    actor.ailment = ailment
    return True

  def dispel_ailment(actor):
    actor.ailment = None
    actor.ailment_turns = 0

  def wake_up(actor):
    actor.stepped = True
    if actor.ailment == "sleep":
      actor.ailment = None

  def kill(actor):
    actor.core.kill()
    actor.ailment = None
    actor.ailment_turns = 0

  def revive(actor, hp_factor=0):
    actor.core.revive(hp_factor)

  def promote(actor):
    actor.rare = True
    actor.core.hp_max += 5
    actor.core.hp += 5
    actor.core.st += 2
    actor.core.en += 2

  def regen(actor, amount=None):
    if amount is None:
      amount = actor.get_hp_max() / 200
    actor.set_hp(min(actor.get_hp_max(), actor.get_hp() + amount))

  def attack(actor, target, damage=None):
    if damage == None:
      damage = DungeonActor.find_damage(actor, target)
    return actor.damage(damage)

  def damage(target, damage):
    target.set_hp(target.get_hp() - damage)
    if target.get_hp() <= 0:
      target.kill()
    elif target.ailment == "sleep" and random.randint(0, 1):
      target.wake_up()
    return damage

  def find_damage(actor, target, modifier=0):
    st = actor.core.st + modifier
    en = target.core.en if target.ailment != "sleep" else 0
    variance = 1 if actor.core.faction == "enemy" else 2
    return max(0, st - en) + random.randint(-variance, variance)

  def step(actor, game):
    enemy = game.find_closest_enemy(actor)
    if enemy is None:
      return False
    if is_adjacent(actor.cell, enemy.cell):
      game.attack(actor, enemy)
    else:
      game.move_to(actor, enemy.cell)
    return True

  def render(actor, sprite, anims=[]):
    new_color = None
    asleep = actor.ailment == "sleep"
    sprites = use_assets().sprites
    anim_group = [a for a in anims[0] if a.target is actor] if anims else []
    for anim in anim_group:
      if type(anim) is AwakenAnim and anim.visible:
        asleep = True
      elif type(anim) is FlinchAnim and anim.time <= 2:
        return None
      elif type(anim) is FlickerAnim and not anim.visible:
        return None
    else:
      if actor.ailment == "poison":
        new_color = palette.PURPLE
      elif actor.core.faction == "player":
        new_color = palette.BLUE
      elif actor.core.faction == "ally":
        new_color = palette.GREEN
      elif actor.core.faction == "enemy" and actor.rare:
        new_color = palette.GOLD_DARK
      elif actor.core.faction == "enemy":
        new_color = palette.RED
    if asleep:
      sprite = darken(sprite)
    elif new_color:
      sprite = replace_color(sprite, palette.BLACK, new_color)
    return sprite

  def color(actor):
    if actor.core.faction == "player": return palette.BLUE
    if actor.core.faction == "enemy" and actor.rare: return palette.GOLD_DARK
    if actor.core.faction == "enemy": return palette.RED

  def token(actor):
    return Token(text=actor.get_name().upper(), color=actor.color())
