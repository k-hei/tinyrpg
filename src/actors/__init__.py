import random

class Actor:
  def __init__(actor, name, faction, hp, st, en, skill=None):
    actor.name = name
    actor.hp_max = hp
    actor.hp = hp
    actor.st = st
    actor.en = en
    actor.skill = skill
    actor.dead = False
    actor.stun = False
    actor.asleep = False
    actor.counter = False
    actor.idle = False
    actor.facing = (1, 0)
    actor.faction = faction
    actor.visible_cells = []

  def regen(actor, amount=1/100):
    if actor.hp + amount < actor.hp_max:
      actor.hp += amount
    else:
      actor.hp = actor.hp_max

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
    if damage < target.hp:
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
    return max(0, st - en)

  def use_skill(actor, game, on_end=None):
    skill = actor.skill
    if skill is None:
      return None
    if game.sp >= skill.cost:
      game.sp -= skill.cost
    return skill.effect(game, on_end=on_end)
