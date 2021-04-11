class Actor:
  def __init__(actor, kind, cell):
    actor.kind = kind
    actor.cell = cell
    actor.hp_max = 5
    actor.hp = actor.hp_max
    actor.dead = False
    actor.facing = (1, 0)
    actor.visible_cells = []

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
  return 3
