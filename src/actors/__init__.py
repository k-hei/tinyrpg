import random
from element import Element
from functools import reduce
from operator import add

import palette
from assets import load as use_assets
from filters import replace_color
from anims.awaken import AwakenAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from cell import is_adjacent, manhattan

class Actor(Element):
  POISON_DURATION = 5
  POISON_STRENGTH = 1 / 6
  skill = None

  def __init__(actor, name, faction, hp, st, en, skills=[]):
    super().__init__(name)
    actor.hp_max = hp
    actor.hp = hp
    actor.st = st
    actor.en = en
    actor.skills = skills
    actor.solid = True
    actor.stepped = False
    actor.dead = False
    actor.ailment = None
    actor.ailment_turns = 0
    actor.counter = False
    actor.idle = False
    actor.rare = False
    actor.facing = (1, 0)
    actor.faction = faction
    actor.visible_cells = []

  def get_skill_hp(actor):
    passive_hps = [s.hp for s in actor.skills if s.kind == "passive"]
    return reduce(add, passive_hps) if passive_hps else 0

  def get_hp(actor):
    return actor.hp + actor.get_skill_hp()

  def get_hp_max(actor):
    return actor.hp_max + actor.get_skill_hp()

  def promote(actor):
    actor.rare = True
    actor.hp_max += 5
    actor.hp += 5
    actor.st += 2
    actor.en += 2

  def regen(actor, amount=None):
    if amount is None:
      amount = actor.get_hp_max() / 200
    actor.hp = min(actor.hp_max, actor.hp + amount)

  def face(actor, dest):
    actor_x, actor_y = actor.cell
    dest_x, dest_y = dest
    delta_x = dest_x - actor_x
    delta_y = dest_y - actor_y
    if abs(delta_x) >= abs(delta_y):
      actor.facing = (int(delta_x / abs(delta_x) if delta_x else 0), 0)
    else:
      actor.facing = (0, int(delta_y / abs(delta_y) if delta_y else 0))

  def inflict(actor, ailment):
    if ailment == actor.ailment:
      return False
    if ailment == "poison":
      actor.ailment_turns = Actor.POISON_DURATION
    actor.ailment = ailment
    return True

  def wake_up(actor):
    actor.stepped = True
    if actor.ailment == "sleep":
      actor.ailment = None

  def move(actor, delta, stage):
    pass

  def attack(actor, target, damage=None):
    if damage == None:
      damage = Actor.find_damage(actor, target)
    return actor.damage(damage)

  def damage(target, damage):
    target.hp -= damage
    if target.ailment == "sleep" and random.randint(0, 1):
      target.wake_up()
    if target.get_hp() <= 0:
      target.dead = True
    return damage

  def find_damage(actor, target):
    st = actor.st
    en = target.en if target.ailment != "sleep" else 0
    variance = 1 if actor.faction == "enemy" else 2
    return max(0, st - en) + random.randint(-variance, variance)

  def step(actor, game):
    enemy = game.find_closest_enemy(actor)
    if enemy is None:
      return False

    if is_adjacent(actor.cell, enemy.cell):
      game.log.print(actor.name.upper() + " attacks")
      game.attack(actor, enemy)
    else:
      game.move_to(actor, enemy.cell)

    return True

  def render(actor, sprite, anims=[]):
    new_color = None
    sprites = use_assets().sprites
    anim_group = [a for a in anims[0] if a.target is actor] if anims else []
    for anim in anim_group:
      if type(anim) is AwakenAnim and anim.visible:
        new_color = palette.PURPLE
        break
      elif type(anim) is FlinchAnim and anim.time <= 2:
        return None
      elif type(anim) is FlickerAnim and not anim.visible:
        return None
    else:
      if actor.ailment == "sleep":
        new_color = palette.PURPLE
      elif actor.ailment == "poison":
        new_color = palette.GREEN_DARK
      elif actor.faction == "player":
        new_color = palette.BLUE
      elif actor.faction == "ally":
        new_color = palette.GREEN
      elif actor.faction == "enemy" and actor.rare:
        new_color = palette.GOLD_DARK
      elif actor.faction == "enemy":
        new_color = palette.RED
    if new_color:
      sprite = replace_color(sprite, palette.BLACK, new_color)
    return sprite
