from random import random, randint
from lib.direction import invert as invert_direction
from dungeon.actors import DungeonActor
from config import HIT_CHANCE, CRIT_CHANCE

def find_damage(actor, target, modifier=1):
  actor_st = actor.st * modifier
  target_en = target.en
  variance = 1
  return max(1, actor_st - target_en + randint(-variance, variance))

def roll(dx, ag, chance):
  if dx >= ag:
    chance = chance + (dx - ag) / 100
  elif ag >= dx * 2:
    chance = dx / ag * chance * 0.75
  else:
    chance = dx / ag * chance
  return random() <= chance

def roll_hit(attacker, defender):
  return roll(
    dx=attacker.stats.dx + attacker.stats.lu / 2,
    ag=defender.stats.ag + defender.stats.lu / 2,
    chance=HIT_CHANCE
  )

def find_miss(actor, target):
  return (
    not target.is_immobile()
    and target.facing != actor.facing
    and (target.aggro > 1 or target.faction == "player")
    and not roll_hit(attacker=actor, defender=target)
  )

def roll_crit(attacker, defender):
  return roll(
    dx=attacker.stats.dx + attacker.stats.lu / 2,
    ag=defender.stats.ag + defender.stats.lu / 2,
    chance=CRIT_CHANCE
  )

def find_crit(actor, target):
  return target.ailment != DungeonActor.AILMENT_FREEZE and (
    target.ailment == DungeonActor.AILMENT_SLEEP
    or actor.facing == target.facing
    or roll_crit(attacker=actor, defender=target)
  )

def can_block(defender, attacker):
  return (
    defender.find_shield()
    and not defender.is_immobile()
    and defender.facing == invert_direction(attacker.facing)
  )
