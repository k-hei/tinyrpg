from random import randint
from pygame import Surface
from sprite import Sprite
from copy import copy

from dungeon.element import DungeonElement
from cores import Core
from skills.weapon import Weapon

from colors.palette import BLACK, WHITE, RED, GREEN, BLUE, CYAN, VIOLET, GOLD, DARKBLUE
from assets import assets
from filters import replace_color, darken_image
from anims.move import MoveAnim
from anims.attack import AttackAnim
from anims.jump import JumpAnim
from anims.awaken import AwakenAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from anims.bounce import BounceAnim
from anims.frame import FrameAnim
from lib.cell import is_adjacent, manhattan, add as add_vector
from lib.lerp import lerp
from comps.log import Token
from config import TILE_SIZE

class DungeonActor(DungeonElement):
  POISON_DURATION = 5
  POISON_STRENGTH = 1 / 7
  FREEZE_DURATION = 5
  SLEEP_DURATION = 256
  skill = None
  drops = []

  class SleepAnim(FrameAnim):
    frames = assets.sprites["status_sleep"]
    frames_duration = 15

  class PoisonAnim(FrameAnim):
    frames = assets.sprites["status_poison"]
    frames_duration = 15

  def __init__(actor, core, hp=None, faction=None, facing=None, ailment=None, ailment_turns=0):
    super().__init__(solid=True, opaque=False)
    actor.core = core
    actor.stats = copy(core.stats)
    actor.set_hp(hp or core.hp)
    actor.set_faction(faction or core.faction)
    actor.set_facing(facing or core.facing)

    actor.anims = []
    actor.ailment = None
    actor.ailment_turns = 0
    if ailment:
      actor.inflict_ailment(ailment)
      actor.ailment_turns = ailment_turns or actor.ailment_turns

    actor.weapon = actor.find_weapon()
    actor.command = None
    actor.counter = False
    actor.turns = 0
    actor.aggro = False
    actor.rare = False
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
    return not actor.command and not actor.is_immobile()
  def is_immobile(actor):
    return actor.is_dead() or actor.ailment in ("sleep", "freeze")

  def get_str(actor):
    return actor.stats.st + (actor.weapon.st if actor.weapon else 0)

  def get_def(actor, stage=None):
    if actor.ailment == "sleep":
      return actor.stats.en // 2
    if actor.ailment == "freeze":
      return int(actor.stats.en * 1.5)
    return actor.stats.en

  def encode(actor):
    cell, name, *props = super().encode()
    props = {
      **(props and props[0] or {}),
      **(actor.get_hp() != actor.get_hp_max() and { "hp": actor.get_hp() } or {}),
      **(actor.get_facing() != (1, 0) and { "facing": actor.get_facing() } or {}),
      **(actor.get_faction() != "player" and { "faction": actor.get_faction() } or {}),
      **(actor.ailment and { "ailment": actor.ailment } or {}),
      **(actor.ailment_turns and { "ailment_turns": actor.ailment_turns } or {}),
      **(actor.rare and { "rare": actor.rare } or {}),
      **({ "message": actor.core.message[0] } if type(actor.core.message) is tuple else {}),
    }
    return [actor.cell, type(actor).__name__, *(props and [props] or [])]

  def find_weapon(actor):
    return next((s for s in actor.core.skills if s.kind == "weapon"), None)

  def find_shield(actor):
    return next((s for s in actor.core.skills if s.kind == "armor" and s.element == "shield"), None)

  def allied(actor, target):
    if target is None or not isinstance(target, DungeonActor):
      return False
    else:
      return Core.allied(actor.core, target.core)

  def get_facing(actor):
    return actor.facing

  def set_facing(actor, facing):
    facing = tuple(map(int, facing))
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
    actor.core.anims = []
    if ailment == "poison":
      actor.ailment_turns = DungeonActor.POISON_DURATION
      actor.anims = [DungeonActor.PoisonAnim()]
    if ailment == "sleep":
      actor.ailment_turns = DungeonActor.SLEEP_DURATION
      actor.anims = [DungeonActor.SleepAnim()]
      if "SleepAnim" in dir(actor.core):
        actor.core.anims = [actor.core.SleepAnim()]
    if ailment == "freeze":
      actor.ailment_turns = DungeonActor.FREEZE_DURATION
    actor.ailment = ailment
    return True

  def step_ailment(actor, game):
    if actor.ailment_turns == 0:
      actor.dispel_ailment()
      return
    actor.ailment_turns -= 1
    if actor.ailment == "sleep":
      actor.regen(actor.get_hp_max() / 50)
    elif actor.ailment == "poison":
      damage = int(actor.get_hp_max() * DungeonActor.POISON_STRENGTH)
      game.flinch(actor, damage, delayed=True)

  def dispel_ailment(actor):
    if actor.ailment == "sleep":
      sleep_anim = next((a for a in actor.anims if type(a) is DungeonActor.SleepAnim), None)
      sleep_anim and actor.anims.remove(sleep_anim)
      if "SleepAnim" in dir(actor.core):
        sleep_anim = next((a for a in actor.core.anims if type(a) is actor.core.SleepAnim), None)
        actor.core.anims.remove(sleep_anim)

    if actor.ailment == "poison":
      poison_anim = next((a for a in actor.anims if type(a) is DungeonActor.PoisonAnim), None)
      poison_anim and actor.anims.remove(poison_anim)

    actor.ailment = None
    actor.ailment_turns = 0

  def wake_up(actor):
    actor.command = True
    if actor.ailment == "sleep":
      actor.dispel_ailment()

  def block(actor):
    pass

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
      actor.core.stats.hp += 5
      actor.core.hp += 5
    actor.core.stats.st += 1
    actor.core.stats.en += 1
    actor.stats = copy(actor.core.stats)

  def regen(actor, amount=None):
    if amount is None:
      amount = actor.get_hp_max() / 200
    actor.set_hp(min(actor.get_hp_max(), actor.get_hp() + amount))

  def effect(actor, game):
    if actor.is_immobile():
      return None
    return actor.talk(game)

  def talk(actor, game):
    game.talkee = actor
    message = actor.core.message
    if type(message) is tuple:
      _, message = message
    if callable(message):
      message = message(game)
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
    if is_adjacent(actor.cell, enemy.cell) and actor.elev == enemy.elev:
      return ("attack", enemy)
    else:
      return ("move_to", enemy.cell)

  def update(actor):
    for anim in actor.anims:
      if anim.done:
        actor.anims.remove(anim)
      else:
        anim.update()
    return actor.core.update()

  def view(actor, sprites, anims=[]):
    if not sprites:
      return []
    if type(sprites) is Surface:
      sprites = [Sprite(image=sprites)]
    if type(sprites) is list:
      sprites = [(Sprite(image=s) if type(s) is Surface else s) for s in sprites]
    sprite = sprites[0]
    offset_x, offset_y, offset_z = (0, 0, 0)
    actor_width, actor_height = (TILE_SIZE, TILE_SIZE)
    actor_cell = actor.cell
    new_color = None
    asleep = actor.ailment == "sleep"
    anim_group = ([a for a in anims[0] if a.target is actor] if anims else []) + actor.core.anims
    for anim in anim_group:
      if type(anim) is AwakenAnim and anim.visible:
        asleep = True
      if type(anim) is AttackAnim or type(anim) is JumpAnim and anim.cell:
        offset_x, offset_y = actor.get_move_offset(anim)
      if type(anim) is FlinchAnim and anim.time <= 3:
        return []
      if type(anim) is FlinchAnim:
        offset_x, offset_y = anim.offset
        if actor.ailment == "freeze" and anim.time % 2:
          sprites.append(Sprite(
            image=replace_color(assets.sprites["fx_icecube"], BLACK, CYAN),
            layer="elems"
          ))
      if type(anim) is BounceAnim:
        anim_xscale, anim_yscale = anim.scale
        actor_width *= anim_xscale
        actor_height *= anim_yscale
      if isinstance(anim, FrameAnim):
        sprite.image = anim.frame()
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

    if actor.ailment:
      badge_image = None
      badge_pos = (12, -20)
      move_anim = next((a for a in anim_group if type(a) is MoveAnim), None)
      if move_anim:
        badge_pos = add_vector(badge_pos, actor.get_move_offset(move_anim))

      if actor.ailment == "sleep":
        sleep_anim = next((a for a in actor.anims if type(a) is DungeonActor.SleepAnim), None)
        if sleep_anim:
          badge_image = sleep_anim.frame()
          badge_image = replace_color(badge_image, BLACK, DARKBLUE)

      if actor.ailment == "poison":
        poison_anim = next((a for a in actor.anims if type(a) is DungeonActor.PoisonAnim), None)
        if poison_anim:
          badge_image = poison_anim.frame()
          badge_image = replace_color(badge_image, BLACK, VIOLET)
          badge_image = replace_color(badge_image, WHITE, DARKBLUE)

      if badge_image:
        sprites.append(Sprite(
          image=badge_image,
          pos=badge_pos,
          origin=("left", "bottom"),
          layer="vfx"
        ))

    move_anim = next((a for a in anim_group if type(a) is MoveAnim), None)
    if actor.elev > 0 and not move_anim:
      offset_z = actor.elev * TILE_SIZE

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
    sprite.move((offset_x, offset_y - offset_z))
    sprite.size = (actor_width, actor_height)
    offset_y = abs(
      move_anim
      and (len(move_anim.src) != 3
        or move_anim.src[2] == move_anim.dest[2])
      and actor.get_move_offset(move_anim)[1]
      or 0)
    sprite.offset += offset_z + offset_y
    return super().view(sprites, anims)

  def color(actor):
    if actor.core.faction == "player": return BLUE
    if actor.core.faction == "enemy" and actor.rare: return GOLD
    if actor.core.faction == "enemy": return RED
    if actor.core.faction == "ally": return actor.core.color or GREEN

  def token(actor):
    return Token(text=actor.get_name().upper(), color=actor.color())
