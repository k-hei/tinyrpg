from dataclasses import dataclass
from functools import reduce
from operator import add
from pygame import Surface
from pygame.transform import flip
from palette import BLACK, RED, GREEN, BLUE, GOLD_DARK
from filters import replace_color
from comps.log import Token

class Core:
  def __init__(core, name, faction="ally", facing=(1, 0), hp=0, st=0, en=0, skills=[], message=None):
    core.name = name
    core.faction = faction
    core.facing = facing
    core.hp = hp
    core.hp_max = hp
    core.st = st
    core.en = en
    core.skills = skills
    core.message = message
    core.dead = False
    core.anims = []
    core.color = None

  def rename(core, name):
    core.name = name

  def get_hp(core):
    return core.hp + core.get_skill_hp()

  def get_hp_max(core):
    return core.hp_max + core.get_skill_hp()

  def set_hp(core, hp):
    core.hp = hp - core.get_skill_hp()

  def get_skill_hp(core):
    passive_hps = [s.hp for s in core.skills if s.kind == "armor"]
    return reduce(add, passive_hps) if passive_hps else 0

  def get_active_skills(core):
    return [s for s in core.skills if s.kind != "armor"]

  def kill(core):
    core.set_hp(0)
    core.dead = True

  def revive(core, hp_factor):
    if hp_factor == 0:
      revive_hp = 1
    else:
      revive_hp = core.get_hp_max() * hp_factor
    core.set_hp(revive_hp)
    core.dead = False

  def allied(a, b):
    return (a.faction == b.faction
      or a.faction == "player" and b.faction == "ally"
      or a.faction == "ally" and b.faction == "player")

  def color(core):
    if core.faction == "player": return BLUE
    if core.faction == "enemy": return RED

  def token(core):
    return Token(text=core.name.upper(), color=core.color())

  def update(core):
    for anim in core.anims:
      if anim.done:
        core.anims.remove(anim)
      anim.update()

  def view(core, sprites):
    if not sprites:
      return []
    if core.color:
      COLOR = core.color
    elif core.faction == "player":
      COLOR = BLUE
    elif core.faction == "ally":
      COLOR = GREEN
    elif core.faction == "enemy":
      COLOR = RED
    sprite = sprites[0]
    sprite.image = replace_color(sprite.image, BLACK, COLOR)
    return sprites
