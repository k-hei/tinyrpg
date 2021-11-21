from random import randint
from pygame import Surface
from lib.sprite import Sprite
from copy import copy

from dungeon.element import DungeonElement
from cores import Core
from skills.weapon import Weapon

from colors import darken_color
from colors.palette import BLACK, WHITE, GRAY, RED, GREEN, BLUE, CYAN, VIOLET, GOLD, DARKBLUE
from assets import assets
from lib.filters import replace_color, darken_image
from anims.move import MoveAnim
from anims.attack import AttackAnim
from anims.jump import JumpAnim
from anims.awaken import AwakenAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from anims.bounce import BounceAnim
from anims.frame import FrameAnim
from anims.drop import DropAnim
from anims.warpin import WarpInAnim
from lib.cell import is_adjacent, manhattan, add as add_vector
from lib.lerp import lerp
from comps.log import Token
from comps.hpbubble import HpBubble
from vfx.icepiece import IcePieceVfx
import config
from config import TILE_SIZE

from contexts import Context
from contexts.dialogue import DialogueContext

class DungeonActor(DungeonElement):
  POISON_DURATION = 5
  POISON_STRENGTH = 1 / 7
  FREEZE_DURATION = 7
  SLEEP_DURATION = 256
  INVULNERABLE_DURATION = 16
  COOLDOWN_DURATION = 1
  VISION_RANGE = config.VISION_RANGE

  AI_MOVE = "move"
  AI_LOOK = "look"

  active = True
  solid = True
  skill = None
  drops = []

  class SleepAnim(FrameAnim):
    frames = assets.sprites["status_sleep"]
    frames_duration = 15
    loop = True

  class PoisonAnim(FrameAnim):
    frames = assets.sprites["status_poison"]
    frames_duration = 15
    loop = True

  def __init__(
    actor,
    core,
    hp=None,
    faction=None,
    rare=False,
    behavior="chase",
    facing=None,
    floating=False,
    aggro=0,
    ailment=None,
    ailment_turns=0,
    charge_skill=None,
    charge_dest=None,
    charge_turns=0,
    charge_cooldown=0,
  ):
    super().__init__(solid=True, opaque=False)
    actor.core = core
    actor.stats = copy(core.stats)
    actor.set_hp(hp or core.hp)
    actor.behavior = behavior
    actor.bubble = HpBubble(actor.core)

    actor.anims = []
    actor.floating = floating
    actor.aggro = aggro
    actor.ailment = None
    actor.ailment_turns = 0
    if ailment:
      actor.inflict_ailment(ailment)
      actor.ailment_turns = ailment_turns or actor.ailment_turns

    actor.charge_cooldown = charge_cooldown
    if charge_skill:
      actor.charge(skill=charge_skill, dest=charge_dest, turns=charge_turns)
    else:
      actor.reset_charge()

    actor.weapon = actor.find_weapon()
    actor.item = None
    actor.command = None
    actor.counter = False
    actor.turns = 0
    actor.updates = 0
    actor.rare = rare
    actor.visible_cells = []
    actor.on_defeat = None
    actor.flipped = False

    actor.ai_mode = None
    actor.ai_target = None
    actor.ai_path = None

    if rare:
      actor.promote()

  @property
  def name(actor):
    return actor.core.name

  @property
  def faction(actor):
    return actor.core.faction

  @faction.setter
  def faction(actor, faction):
    actor.core.faction = faction
    actor.reset_charge()

  @property
  def facing(actor):
    return actor.core.facing

  @facing.setter
  def facing(actor, facing):
    actor.core.facing = facing and tuple(map(int, facing))

  def face(actor, dest):
    actor_x, actor_y = actor.cell
    dest_x, dest_y = dest
    delta_x = dest_x - actor_x
    delta_y = dest_y - actor_y
    if abs(delta_x) >= abs(delta_y):
      facing = (int(delta_x / (abs(delta_x) or 1)), 0)
    else:
      facing = (0, int(delta_y / (abs(delta_y) or 1)))
    actor.facing = facing

  def get_hp(actor): return actor.core.get_hp()
  def get_hp_max(actor): return actor.core.get_hp_max()
  def set_hp(actor, hp): actor.core.set_hp(hp)
  def get_skills(actor): return actor.core.skills
  def get_active_skills(actor): return actor.core.get_active_skills()
  def is_dead(actor): return actor.core.dead
  def can_step(actor):
    return not actor.command and not actor.is_immobile()
  def is_immobile(actor):
    return actor.is_dead() or actor.ailment in ("sleep", "freeze") or actor.charge_skill

  def get_str(actor):
    return actor.stats.st + (actor.weapon.st if actor.weapon else 0)

  def get_def(actor, stage=None):
    if actor.ailment == "sleep":
      return actor.stats.en // 2
    if actor.ailment == "freeze":
      return int(actor.stats.en * 1.5)
    return actor.stats.en

  def charge(actor, skill, dest=None, turns=0):
    actor.charge_skill = skill
    actor.charge_dest = dest
    actor.charge_turns = turns or skill.charge_turns
    if "ChargeAnim" in dir(actor):
      actor.core.anims.append(actor.ChargeAnim())

  def reset_charge(actor):
    actor.charge_skill = None
    actor.charge_dest = None
    actor.charge_turns = 0
    actor.core.anims.clear()

  def discharge(actor):
    if actor.charge_skill is None or actor.charge_cooldown:
      return None
    command = ("use_skill", actor.charge_skill, actor.charge_dest)
    actor.charge_cooldown = actor.COOLDOWN_DURATION
    actor.reset_charge()
    return command

  def step_charge(actor):
    if actor.charge_cooldown:
      actor.charge_cooldown -= 1
    if actor.charge_turns:
      actor.charge_turns -= 1
      if actor.charge_turns == 0:
        return actor.discharge()
      else:
        return ("wait",)

  def alert(actor, cell=None):
    actor.ai_target = cell
    actor.ai_mode = DungeonActor.AI_MOVE
    if actor.aggro == 0:
      actor.aggro = 1
      actor.turns = 0

  def encode(actor):
    cell, name, *props = super().encode()
    props = {
      **(props and props[0] or {}),
      **(actor.get_hp() != actor.get_hp_max() and { "hp": actor.get_hp() } or {}),
      **(actor.facing != (1, 0) and { "facing": actor.facing } or {}),
      **(actor.faction != "player" and { "faction": actor.faction } or {}),
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

  def inflict_ailment(actor, ailment):
    actor.core.anims = []
    if ailment == "poison":
      if actor.ailment == "poison":
        return False
      actor.ailment_turns = DungeonActor.POISON_DURATION
      actor.anims = [DungeonActor.PoisonAnim()]
    elif ailment == "sleep":
      if actor.ailment == "sleep":
        return False
      actor.ailment_turns = 16 if actor.faction == "player" else DungeonActor.SLEEP_DURATION
      actor.anims = [DungeonActor.SleepAnim()]
      if "SleepAnim" in dir(actor.core):
        actor.core.anims = [actor.core.SleepAnim()]
    elif ailment == "freeze":
      actor.ailment_turns = DungeonActor.FREEZE_DURATION
    elif ailment == "invulnerable":
      actor.ailment_turns = DungeonActor.INVULNERABLE_DURATION
      actor.stats.st += 2
      actor.stats.dx += 10
      actor.stats.ag *= 2
      actor.stats.en += 2
      actor.stats.lu += 10
    actor.ailment = ailment
    return True

  def step_status(actor, game):
    if actor.aggro and not actor.ailment == "freeze":
      actor.aggro += 1
    actor.ailment_turns -= 1
    if actor.ailment == "poison":
      damage = int(actor.get_hp_max() * DungeonActor.POISON_STRENGTH)
      return game.flinch(actor, damage, delayed=True, on_end=actor.dispel_ailment if actor.ailment_turns == 0 else None)
    if actor.ailment == "sleep":
      actor.regen(actor.get_hp_max() / 50)
    if actor.ailment_turns == 0:
      if actor.ailment == "freeze":
        game.vfx += [IcePieceVfx( # this belongs in actor view
          pos=tuple([(x + 0.5) * TILE_SIZE for x in actor.cell]),
        ) for _ in range(randint(3, 4))]
      actor.dispel_ailment()
      game.anims.append([AwakenAnim(target=actor)])

  def dispel_ailment(actor):
    if actor.ailment == "sleep":
      return actor.wake_up()

    if actor.ailment == "poison":
      poison_anim = next((a for a in actor.anims if type(a) is DungeonActor.PoisonAnim), None)
      poison_anim and actor.anims.remove(poison_anim)

    if actor.ailment == "invulnerable":
      actor.stats = copy(actor.core.stats)

    actor.ailment = None
    actor.ailment_turns = 0

  def wake_up(actor):
    if actor.ailment != "sleep":
      return False
    actor.ailment = None
    actor.ailment_turns = 0
    sleep_anim = next((a for a in actor.anims if type(a) is DungeonActor.SleepAnim), None)
    sleep_anim and actor.anims.remove(sleep_anim)
    if "SleepAnim" in dir(actor.core):
      sleep_anim = next((a for a in actor.core.anims if type(a) is actor.core.SleepAnim), None)
      if sleep_anim:
        actor.core.anims.remove(sleep_anim)
    actor.turns = 0
    return True

  def block(actor):
    pass

  def kill(actor, game=None):
    actor.core.kill()
    actor.core.anims = []

  def revive(actor, hp_factor=0):
    actor.core.revive(hp_factor)
    actor.ailment = None
    actor.ailment_turns = 0

  def promote(actor, hp=True):
    actor.rare = True
    if hp:
      actor.core.stats.hp += 5
      actor.core.hp += 5
    actor.core.stats.st += 1
    actor.core.stats.en += 1
    actor.core.stats.ag += 4
    actor.stats = copy(actor.core.stats)

  def regen(actor, amount=None):
    if amount is None:
      amount = actor.get_hp_max() / 200
    actor.set_hp(min(actor.get_hp_max(), actor.get_hp() + amount))

  def effect(actor, game, trigger):
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
    game.camera.focus(((hero_x + actor_x) / 2, (hero_y + actor_y) / 2 + 1), speed=8)
    def stop_talk():
      if actor in game.floor.elems:
        actor.face(old_target)
      game.camera.blur()
      game.talkee = None
    if isinstance(message, Context):
      context = message
    else:
      context = DialogueContext(script=message)
    game.open(context, on_close=stop_talk)

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
    elif target.ailment == "sleep":
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
    if not enemy:
      return None
    if not actor.aggro:
      if enemy and game.is_cell_in_vision_range(actor, cell=enemy.cell):
        if actor.faction == "ally":
          print("alert ally from actor step")
        actor.alert(cell=enemy.cell)
      return None
    if is_adjacent(actor.cell, enemy.cell) and actor.elev == enemy.elev:
      return ("attack", enemy)
    else:
      return ("move_to", enemy.cell)

  def update(actor, game):
    actor.updates += 1
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
    actor_width, actor_height = sprite.image.get_size()
    actor_cell = actor.cell
    asleep = actor.ailment == "sleep"
    anim_group = [a for a in anims[0] if a.target is actor] if anims else []
    anim_group += actor.core.anims
    for anim in anim_group:
      if type(anim) is AwakenAnim and anim.visible:
        asleep = True
      if type(anim) is AttackAnim and anim.cell:
        offset_x, offset_y = actor.find_move_offset(anim)
      if type(anim) is FlinchAnim and anim.time > 0 and anim.time <= 3:
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

    warpin_anim = next((a for a in anim_group if type(a) is WarpInAnim), None)
    drop_anim = next((a for a in anim_group if type(a) is DropAnim), None)
    move_anim = next((a for a in anim_group if isinstance(a, MoveAnim)), None)
    move_offset = actor.find_move_offset(anims)

    if actor.elev > 0 and not move_anim:
      offset_z = actor.elev * TILE_SIZE

    # ailment badge
    if actor.ailment and not drop_anim:
      badge_image = None
      badge_pos = (4, -20 - offset_z)
      badge_pos = add_vector(badge_pos, move_offset)

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

    # hp bubble
    if actor.faction != "player" and not (actor.faction == "ally" and actor.behavior == "guard"):
      bubble_sprites = actor.bubble.view()
      actor.bubble.color = actor.color()
      for bubble_sprite in bubble_sprites:
        bubble_sprite.move((24, -21 - offset_z))
        bubble_sprite.move(move_offset)
      sprites += bubble_sprites

    # aggro icon
    if actor.aggro in (1, 2) and actor.faction == "enemy" and not actor.ailment == "freeze" and not warpin_anim:
      marker_image = assets.sprites["aggro_mark"]
      marker_image = replace_color(marker_image, BLACK, RED)
      marker_sprite = Sprite(
        image=marker_image,
        pos=add_vector((-14, -24 - offset_z), move_offset),
        layer="vfx"
      )
      sprites.append(marker_sprite)

    # item icon
    if actor.item:
      item_image = actor.item().render()
      item_sprite = Sprite(
        image=item_image,
        pos=(0, -24),
        layer="vfx"
      )
      item_sprite.move(move_offset)
      sprites += [item_sprite]

    actor_color = actor.color()
    if (not actor.aggro
    and actor.faction != "player"
    and not actor.ailment in ("sleep", "freeze")
    and actor.updates % 60 >= 30
    ):
      actor_color = darken_color(actor_color)
    if actor_color != BLACK:
      sprite.image = replace_color(sprite.image, BLACK, actor_color)
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
      and move_anim.src
      and (len(move_anim.src) != 3
        or move_anim.src[2] == move_anim.dest[2])
      and actor.find_move_offset(move_anim)[1]
      or 0)
    sprite.offset += offset_z + offset_y
    return super().view(sprites, anims)

  def color(actor):
    if actor.ailment == "poison":
      return VIOLET
    elif actor.ailment == "freeze":
      return CYAN
    elif actor.core.faction == "enemy" and actor.rare or actor.ailment == "invulnerable":
      return GOLD
    elif actor.core.faction == "player":
      return BLUE
    elif actor.core.faction == "ally":
      return GREEN
    elif actor.core.faction == "enemy":
      return RED
    return GRAY

  def token(actor):
    return Token(text=actor.name.upper(), color=actor.color())
