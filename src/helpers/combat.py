from random import random, randint
from lib.direction import invert as invert_direction
from dungeon.actors import DungeonActor
from config import MISS_CHANCE, CRIT_CHANCE


def find_damage(attacker, defender, atk_mod=1):
  attacker_st = attacker.st * atk_mod
  defender_en = defender.en
  variance = 1
  return max(1, attacker_st - defender_en + randint(-variance, variance))

def roll(dx, ag, chance):
  if dx >= ag:
    chance = chance + (dx - ag) / 100
  elif ag >= dx * 2:
    chance = dx / ag * chance * 0.75
  else:
    chance = dx / ag * chance
  return random() <= chance

def roll_miss(attacker, defender):
  return roll(
    dx=attacker.stats.dx + attacker.stats.lu / 2,
    ag=defender.stats.ag + defender.stats.lu / 2,
    chance=MISS_CHANCE
  )

def will_miss(attacker, defender):
  return (
    not defender.is_immobile()
    and defender.facing != attacker.facing
    and (defender.aggro > 1 or defender.faction == "player")
    and roll_miss(attacker, defender)
  )

def roll_crit(attacker, defender, mod=1):
  return roll(
    dx=attacker.stats.dx + attacker.stats.lu / 2,
    ag=defender.stats.ag + defender.stats.lu / 2,
    chance=CRIT_CHANCE * mod,
  )

def will_crit(attacker, defender, mod=1):
  return defender.ailment != DungeonActor.AILMENT_FREEZE and (
    defender.ailment == DungeonActor.AILMENT_SLEEP
    or attacker.facing == defender.facing
    or roll_crit(attacker=attacker, defender=defender, mod=mod)
  )

def will_block(attacker, defender):
  return (
    defender.find_shield()
    and not defender.is_immobile()
    and defender.facing == invert_direction(attacker.facing)
  )


from lib.cell import upscale
from anims.move import MoveAnim
from config import TILE_SIZE

def animate_snap(actor, anims, speed=2, scale=TILE_SIZE, on_end=None):
  x, y = actor.pos
  x += scale / 2
  y += scale / 2
  if x % scale or y % scale:
    actor_dest = upscale(actor.cell, scale)
    actor.stop_move()
    if not anims:
      anims.append([])
    anims[-1].append(MoveAnim(
      target=actor,
      src=actor.pos,
      dest=actor_dest,
      speed=speed,
      on_end=on_end
    ))
    return actor.cell

  if on_end:
    return on_end()
