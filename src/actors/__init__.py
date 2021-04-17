import random
import palette
from functools import reduce
from operator import add

class Actor:
  def __init__(actor, name, faction, hp, st, en, skills=[]):
    actor.name = name
    actor.hp_max = hp
    actor.hp = hp
    actor.st = st
    actor.en = en
    actor.skills = skills
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
    actor.hp = min(actor.get_hp_max(), actor.hp + amount)

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
    if damage < int(target.get_hp()):
      target.hp -= damage
      if target.asleep and random.randint(0, 1):
        target.wake_up()
    else:
      target.hp = 0
      target.dead = True
    return damage

  def find_damage(actor, target):
    st = actor.st
    en = target.en if not target.asleep else 0
    return max(0, st - en) + random.randint(-2, 2)

  def render(actor):
    pass
