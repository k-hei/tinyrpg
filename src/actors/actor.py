class Actor:
  def __init__(actor, name, hp):
    actor.name = name
    actor.hp_max = hp
    actor.hp = hp
    actor.dead = False
    actor.facing = (1, 0)
    actor.visible_cells = []

  def regen(actor):
    if actor.hp < actor.hp_max:
      actor.hp += 1 / 20

  def move(actor, delta, stage):
    pass

  def attack(actor, target, counter=False):
    damage = _find_damage(actor, target)
    if damage < target.hp:
      target.hp -= damage
    else:
      target.hp = 0
      target.dead = True
    return damage

def _find_damage(actor, target):
  return 2
