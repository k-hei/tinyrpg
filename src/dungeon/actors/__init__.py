from random import randint
from pygame import Surface
from sprite import Sprite

from dungeon.element import DungeonElement
from cores import Core
from skills.weapon import Weapon

from colors.palette import BLACK, RED, GREEN, BLUE, CYAN, VIOLET, GOLD
from assets import load as use_assets
from filters import replace_color, darken_image
from anims.move import MoveAnim
from anims.attack import AttackAnim
from anims.jump import JumpAnim
from anims.awaken import AwakenAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from anims.bounce import BounceAnim
from anims.frame import FrameAnim
from lib.cell import is_adjacent, manhattan
from lib.lerp import lerp
from comps.log import Token
from config import TILE_SIZE

class DungeonActor(DungeonElement):
  POISON_DURATION = 4
  POISON_STRENGTH = 1 / 7
  FREEZE_DURATION = 5
  SLEEP_DURATION = 256
  skill = None
  drops = []

  def __init__(actor, core, ailment=None):
    super().__init__(solid=True)
    actor.core = core
    actor.ailment = None
    actor.ailment_turns = 0
    if ailment:
      actor.inflict_ailment(ailment)
    actor.weapon = actor.load_weapon()
    actor.stepped = False
    actor.counter = False
    actor.aggro = False
    actor.rare = False
    actor.facing = core.facing or (1, 0)
    actor.visible_cells = []
    actor.on_kill = None
    actor.flipped = False

  def get_name(actor): return actor.core.name
  def get_faction(actor): return actor.core.faction
  def set_faction(actor, faction):
    actor.core.faction = faction

  def get_hp(actor): return actor.core.get_hp()
  def get_hp_max(actor): return actor.core.get_hp_max()
  def set_hp(actor, hp): actor.core.set_hp(hp)
  def get_skills(actor): return actor.core.skills
  def get_active_skills(actor): return actor.core.get_active_skills()
  def is_dead(actor): return actor.core.dead
  def can_step(actor):
    return not actor.is_dead() and not actor.stepped and actor.ailment not in ("sleep", "freeze")

  def get_str(actor):
    return actor.core.st + (actor.weapon.st if actor.weapon else 0)

  def get_def(actor, stage=None):
    if actor.ailment == "sleep":
      return actor.core.en // 2
    if actor.ailment == "freeze":
      return int(actor.core.en * 1.5)
    return actor.core.en

  def load_weapon(actor):
    return next((s for s in actor.core.skills if s.kind == "weapon"), None)

  def allied(actor, target):
    if target is None or not isinstance(target, DungeonActor):
      return False
    else:
      return Core.allied(actor.core, target.core)

  def get_facing(actor):
    return actor.facing

  def set_facing(actor, facing):
    actor.facing = facing
    actor.core.facing = facing

  def face(actor, dest):
    actor_x, actor_y = actor.cell
    dest_x, dest_y = dest
    delta_x = dest_x - actor_x
    delta_y = dest_y - actor_y
    if abs(delta_x) >= abs(delta_y):
      facing = (int(delta_x / (abs(delta_x) or 1)), 0)
    else:
      facing = (0, int(delta_y / (abs(delta_y) or 1)))
    actor.set_facing(facing)

  def inflict_ailment(actor, ailment):
    if ailment == actor.ailment:
      return False
    if ailment == "poison":
      actor.ailment_turns = DungeonActor.POISON_DURATION
    if ailment == "freeze":
      actor.ailment_turns = DungeonActor.FREEZE_DURATION
    if ailment == "sleep":
      actor.ailment_turns = DungeonActor.SLEEP_DURATION
    actor.ailment = ailment
    return True

  def step_ailment(actor):
    if actor.ailment_turns > 0:
      actor.ailment_turns -= 1
    else:
      actor.dispel_ailment()

  def dispel_ailment(actor):
    actor.ailment = None
    actor.ailment_turns = 0

  def wake_up(actor):
    actor.stepped = True
    if actor.ailment == "sleep":
      actor.ailment = None

  def kill(actor):
    actor.core.kill()
    actor.core.anims = []
    actor.ailment = None
    actor.ailment_turns = 0

  def revive(actor, hp_factor=0):
    actor.core.revive(hp_factor)

  def promote(actor, hp=True):
    actor.rare = True
    if hp:
      actor.core.hp_max += 5
      actor.core.hp += 5
    actor.core.st += 1
    actor.core.en += 1

  def regen(actor, amount=None):
    if amount is None:
      amount = actor.get_hp_max() / 200
    actor.set_hp(min(actor.get_hp_max(), actor.get_hp() + amount))

  def effect(actor, game):
    return actor.talk(game)

  def talk(actor, game):
    game.talkee = actor
    message = actor.core.message
    message = message(game) if callable(message) else message
    if not message:
      game.talkee = None
      return
    hero = game.hero
    hero_x, hero_y = hero.cell
    actor_x, actor_y = actor.cell
    facing_x, facing_y = actor.facing
    old_target = (actor_x + facing_x, actor_y + facing_y)
    actor.face(hero.cell)
    game.camera.focus(((hero_x + actor_x) / 2, (hero_y + actor_y) / 2 + 1))
    def stop_talk():
      if actor in game.floor.elems:
        actor.face(old_target)
      game.camera.blur()
      game.talkee = None
    game.open(message, on_close=stop_talk)

  def move_to(actor, dest):
    actor.cell = dest

  def attack(actor, target, damage=None):
    if damage == None:
      damage = DungeonActor.find_damage(actor, target)
    return actor.damage(damage)

  def damage(target, damage):
    target.set_hp(target.get_hp() - damage)
    if target.get_hp() <= 0:
      target.kill()
    elif target.ailment == "sleep" and randint(0, 1):
      target.wake_up()
    return damage

  def find_damage(actor, target, modifier=1):
    st = actor.get_str() * modifier
    en = target.get_def()
    variance = 1 if actor.core.faction == "enemy" else 2
    return max(1, st - en + randint(-variance, variance))

  def step(actor, game):
    if not actor.can_step():
      return None
    enemy = game.find_closest_enemy(actor)
    if enemy is None:
      return None
    if is_adjacent(actor.cell, enemy.cell):
      return ("attack", enemy)
    else:
      return ("move_to", enemy.cell)

  def update(actor):
    return actor.core.update()

  def view(actor, sprites, anims=[]):
    assets = use_assets().sprites
    if not sprites:
      return []
    if type(sprites) is Surface:
      sprites = [Sprite(image=sprites)]
    if type(sprites) is list:
      sprites = [(Sprite(image=s) if type(s) is Surface else s) for s in sprites]
    sprite = sprites[0]
    offset_x, offset_y = (0, 0)
    actor_width, actor_height = (TILE_SIZE, TILE_SIZE)
    actor_cell = actor.cell
    new_color = None
    asleep = actor.ailment == "sleep"
    anim_group = ([a for a in anims[0] if a.target is actor] if anims else []) + actor.core.anims
    for anim in anim_group:
      if type(anim) is AwakenAnim and anim.visible:
        asleep = True
      if type(anim) is AttackAnim or type(anim) is JumpAnim and anim.cell:
        anim_x, anim_y = anim.cell
        actor_x, actor_y = actor.cell
        offset_x = (anim_x - actor_x) * TILE_SIZE
        offset_y = (anim_y - actor_y) * TILE_SIZE
      if type(anim) is JumpAnim:
        offset_y += anim.offset
      if type(anim) is FlinchAnim and anim.time <= 3:
        return []
      if type(anim) is FlinchAnim:
        offset_x, offset_y = anim.offset
        if actor.ailment == "freeze" and anim.time % 2:
          sprites.append(Sprite(
            image=replace_color(assets["fx_icecube"], BLACK, CYAN),
            layer="elems"
          ))
      if type(anim) is BounceAnim:
        anim_xscale, anim_yscale = anim.scale
        actor_width *= anim_xscale
        actor_height *= anim_yscale
      if isinstance(anim, FrameAnim):
        sprite.image = anim.frame
    else:
      if actor.ailment == "poison":
        new_color = VIOLET
      elif actor.ailment == "freeze":
        new_color = CYAN
      elif actor.core.faction == "player":
        new_color = BLUE
      elif actor.core.faction == "ally":
        new_color = GREEN
      elif actor.core.faction == "enemy" and actor.rare:
        new_color = GOLD
      elif actor.core.faction == "enemy":
        new_color = RED

    if new_color:
      sprite.image = replace_color(sprite.image, BLACK, new_color)
    if asleep:
      sprite.image = darken_image(sprite.image)
    facing_x, _ = actor.facing
    _, flip_y = sprite.flip
    if facing_x == -1:
      actor.flipped = True
    elif facing_x == 1:
      actor.flipped = False
    sprite.flip = (actor.flipped, flip_y)
    sprite.move((offset_x, offset_y))
    sprite.size = (actor_width, actor_height)
    sprite.layer = "elems"
    return super().view(sprites, anims)

  def color(actor):
    if actor.core.faction == "player": return BLUE
    if actor.core.faction == "enemy" and actor.rare: return GOLD
    if actor.core.faction == "enemy": return RED
    if actor.core.faction == "ally": return actor.core.color or GREEN

  def token(actor):
    return Token(text=actor.get_name().upper(), color=actor.color())
