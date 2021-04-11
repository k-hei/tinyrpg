class Actor:
  def __init__(actor, name, faction, hp, st, en):
    actor.name = name
    actor.hp_max = hp
    actor.hp = hp
    actor.st = st
    actor.en = en
    actor.dead = False
    actor.facing = (1, 0)
    actor.faction = faction
    actor.visible_cells = []

  def regen(actor, amount=1/100):
    if actor.hp + amount < actor.hp_max:
      actor.hp += amount
    else:
      actor.hp = actor.hp_max

  def move(actor, delta, stage):
    pass

  def attack(actor, target, counter=False):
    damage = actor.find_damage(target)
    if damage < target.hp // 1:
      target.hp -= damage
    else:
      target.hp = 0
      target.dead = True
    return damage

  def find_damage(actor, target):
    return max(0, actor.st - target.en)
