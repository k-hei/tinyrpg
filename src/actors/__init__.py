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

class Actor(Element):
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
    actor.stun = False
    actor.asleep = False
    actor.counter = False
    actor.idle = False
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

  def regen(actor, amount=None):
    if amount is None:
      amount = actor.get_hp_max() / 200
    actor.hp = min(actor.hp_max, actor.hp + amount)

  def face(actor, facing):
    actor.facing = facing

  def wake_up(actor):
    actor.stun = True
    actor.asleep = False

  def move(actor, delta, stage):
    pass

  def attack(actor, target, damage=None):
    if damage == None:
      damage = Actor.find_damage(actor, target)
    return actor.damage(damage)

  def damage(target, damage):
    target.hp -= damage
    if target.asleep and random.randint(0, 1):
      target.wake_up()
    if target.get_hp() <= 0:
      target.dead = True
    return damage

  def find_damage(actor, target):
    st = actor.st
    en = target.en if not target.asleep else 0
    variance = 1 if actor.faction == "enemy" else 2
    return max(0, st - en) + random.randint(-variance, variance)

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
      if actor.asleep:
        new_color = palette.PURPLE
      elif actor.faction == "player":
        new_color = palette.BLUE
      elif actor.faction == "ally":
        new_color = palette.GREEN
      elif actor.faction == "enemy":
        new_color = palette.RED
    if new_color:
      sprite = replace_color(sprite, palette.BLACK, new_color)
    return sprite
