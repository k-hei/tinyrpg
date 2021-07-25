from dataclasses import dataclass
from functools import reduce
from operator import add
from pygame import Surface
from pygame.transform import flip
from colors.palette import BLACK, RED, GREEN, BLUE, DARKGOLD
from filters import replace_color
from comps.log import Token

@dataclass
class Stats:
  hp: int = 1
  st: int = 1
  ma: int = 1
  en: int = 1
  ag: int = 1
  dx: int = 1
  lu: int = 1

class Core:
  def __init__(core, name, faction="ally", facing=(1, 0), hp=0, stats=Stats(), skills=[], message=None, color=None, anims=None):
    core.name = name
    core.faction = faction
    core.facing = tuple(facing)
    core.hp = hp or stats.hp
    core.bases = stats
    core.stats = stats
    core.skills = skills
    core.color = color
    core.message = message
    core.anims = anims or []
    core.dead = False

  def rename(core, name):
    core.name = name

  def get_hp(core):
    return core.hp + core.get_skill_hp()

  def get_hp_max(core):
    return core.stats.hp + core.get_skill_hp()

  def set_hp(core, hp):
    core.hp = hp - core.get_skill_hp()

  def get_skill_hp(core):
    passive_hps = [s.hp for s in core.skills if s.kind == "armor"]
    return reduce(add, passive_hps) if passive_hps else 0

  def get_active_skills(core):
    return [s for s in core.skills if s.kind != "armor"]

  def heal(core, hp):
    core.set_hp(min(core.get_hp_max(), core.get_hp() + hp))

  def damage(core, hp):
    core.set_hp(core.get_hp() - hp)
    if core.get_hp() <= 0:
      core.kill()

  def kill(core):
    if core.dead:
      return False
    core.set_hp(0)
    core.dead = True
    return True

  def revive(core, hp_factor):
    if not core.dead:
      return False
    if hp_factor == 0:
      revive_hp = 1
    else:
      revive_hp = core.get_hp_max() * hp_factor
    core.set_hp(revive_hp)
    core.dead = False
    return True

  def wake_up(core):
    pass

  def allied(a, b):
    return (a.faction == b.faction
      or a.faction == "player" and b.faction == "ally"
      or a.faction == "ally" and b.faction == "player")

  def get_color(core):
    if core.faction == "player": return BLUE
    if core.faction == "enemy": return RED

  def token(core):
    return Token(text=core.name.upper(), color=core.get_color())

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
