from random import randint, choice
from lib.cell import is_adjacent, neighborhood, add as add_vector
from dungeon.actors import DungeonActor
from dungeon.stage import Tile
from cores import Core, Stats
from assets import sprites
from skills import Skill
from skills.weapon.tackle import Tackle
from skills.armor.hpup import HpUp
from anims.move import MoveAnim
from anims.attack import AttackAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from anims.bounce import BounceAnim
from anims.awaken import AwakenAnim
from anims.shake import ShakeAnim
from anims.pause import PauseAnim
from vfx.alertbubble import AlertBubble
from items.materials.angeltears import AngelTears
from sprite import Sprite
from filters import replace_color
from colors.palette import BLACK, CYAN
from config import PUSH_DURATION

def IdleSprite(facing):
  if facing == (0, 1):
    return sprites["eyeball"]
  elif facing == (0, -1):
    return sprites["eyeball_up"]
  elif facing[0]:
    return sprites["eyeball_right"]

def MoveSprite(facing):
  if facing == (0, 1):
    return sprites["eyeball_move"]
  elif facing == (0, -1):
    return sprites["eyeball_move_up"]
  elif facing[0]:
    return sprites["eyeball_move_right"]

def FlinchSprite(facing):
  if facing == (0, 1):
    return sprites["eyeball_flinch"]
  elif facing == (0, -1):
    return sprites["eyeball_flinch_up"]
  elif facing[0]:
    return sprites["eyeball_flinch_right"]

def ChargeSprite(facing):
  if facing == (0, 1):
    return sprites["eyeball_charge"]
  elif facing == (0, -1):
    return sprites["eyeball_charge_up"]
  elif facing[0]:
    return sprites["eyeball_charge_right"]

def SleepSprite(facing):
  if facing == (0, 1):
    return sprites["eyeball_sleep"]
  elif facing == (0, -1):
    return sprites["eyeball_sleep_up"]
  elif facing[0]:
    return sprites["eyeball_sleep_right"]

class Eyeball(DungeonActor):
  drops = [AngelTears]
  skill = HpUp
  CLONES_MAX = 1
  CLONES_CAN_CLONE = True

  class ChargeAnim(ShakeAnim): pass
  class SplitAnim(MoveAnim): pass
  class Meyetosis(Skill):
    name = "Meyetosis"
    charge_turns = 3
    def effect(user, dest, game, on_end=None):
      neighbors = [c for c in neighborhood(user.cell) if game.floor.is_cell_empty(c)]
      if neighbors:
        user.clones += 1
        neighbor = choice(neighbors)
        clone = Eyeball(
          cloned=True,
          faction=user.faction,
          facing=user.facing,
          aggro=user.aggro,
          rare=user.rare
        )
        game.anims.append([
          BounceAnim(
            duration=20,
            target=user,
            on_squash=lambda: (
              game.floor.spawn_elem_at(neighbor, clone),
              game.anims[0].append(
                Eyeball.SplitAnim(
                  duration=15,
                  target=clone,
                  src=user.cell,
                  dest=neighbor,
                  on_end=on_end
                )
              )
            )
          )
        ])
      else:
        game.anims.append([BounceAnim(
          duration=20,
          target=user,
          on_end=on_end
        )])

  def __init__(eyeball, name="Eyeball", faction="enemy", rare=False, clones=0, cloned=False, *args, **kwargs):
    super().__init__(Core(
      name=name,
      faction=faction,
      stats=Stats(
        hp=17,
        st=12,
        dx=6,
        ag=6,
        lu=3,
        en=11,
      ),
      skills=[Tackle],
      message=[(name, "You looking thick as hell bro! Boutta make me act up. No homo though.")]
    ), *args, **kwargs)
    eyeball.clones = clones
    eyeball.cloned = cloned
    eyeball.wander_phase = "look"
    eyeball.wander_target = eyeball.find_look_turns()
    eyeball.item = None
    if rare:
      eyeball.promote(hp=False)
      eyeball.core.skills.append(HpUp)

  def charge(eyeball, *args, **kwargs):
    super().charge(*args, **kwargs)
    eyeball.core.anims.append(Eyeball.ChargeAnim(magnitude=0.5))

  def discharge(eyeball):
    eyeball.core.anims.clear()
    return super().discharge()

  def find_look_turns(eyeball):
    return randint(2, 6)

  def find_move_target(eyeball, game):
    room = next((r for r in game.floor.rooms if eyeball.cell in r.get_cells()), None)
    if not room:
      return None
    valid_cells = [c for c in room.get_cells() if game.floor.is_cell_empty(c)]
    return choice(valid_cells) if valid_cells else None

  def step_look(eyeball, game):
    if eyeball.wander_target <= 0:
      eyeball.wander_phase = "move"
      eyeball.wander_target = eyeball.find_move_target(game)
      return None
    find_adjacent_facings = lambda facing: (
      facing[0] and [(0, -1), (0, 1)]
      or [(-1, 0), (1, 0)]
    )
    eyeball.facing = choice(find_adjacent_facings(eyeball.facing))
    eyeball.wander_target -= 1
    return None

  def step_move(eyeball, game):
    if not eyeball.wander_target or eyeball.cell == eyeball.wander_target:
      eyeball.wander_phase = "look"
      eyeball.wander_target = eyeball.find_look_turns()
      return None
    delta = game.find_move_to_delta(actor=eyeball, dest=eyeball.wander_target)
    if delta != (0, 0):
      eyeball.facing = delta
      return ("move", delta)

  def step_wander(eyeball, game):
    if eyeball.wander_phase == "look":
      command = eyeball.step_look(game)
    elif eyeball.wander_phase == "move":
      command = eyeball.step_move(game)
    cell = eyeball.cell
    elem = None
    while not Tile.is_opaque(game.floor.get_tile_at(cell)) and elem is None:
      cell = add_vector(cell, eyeball.facing)
      elem = next((e for e in game.floor.get_elems_at(cell) if isinstance(e, DungeonActor) and not eyeball.allied(e)), None)
    if elem:
      eyeball.alert()
      return None
    return command

  def step(eyeball, game):
    if not eyeball.aggro:
      return eyeball.step_wander(game)

    enemy = game.find_closest_enemy(eyeball)
    if (eyeball.core.hp < eyeball.core.stats.hp
    and (not eyeball.cloned or Eyeball.CLONES_CAN_CLONE)
    and eyeball.clones < Eyeball.CLONES_MAX
    and randint(1, 3) == 1):
      return eyeball.charge(Eyeball.Meyetosis)
    elif is_adjacent(eyeball.cell, enemy.cell):
      return ("attack", enemy)
    else:
      return ("move_to", enemy.cell)

  def view(eyeball, anims):
    image = None
    offset_x, offset_y = (0, 0)
    offset_depth = 0
    offset_layer = None
    for anim_group in anims:
      for anim in [a for a in anim_group if a.target is eyeball]:
        if type(anim) is AwakenAnim:
          return super().view(MoveSprite(eyeball.facing), anims)
    if eyeball.is_dead():
      return super().view(FlinchSprite(eyeball.facing), anims)
    anim_group = [a for a in anims[0] if a.target is eyeball] if anims else []
    anim_group += eyeball.core.anims
    for anim in anim_group:
      if isinstance(anim, MoveAnim) and anim.duration != PUSH_DURATION:
        if type(anim) is Eyeball.SplitAnim:
          offset_depth = -16
        image = MoveSprite(eyeball.facing)
        break
      elif (type(anim) is AttackAnim
      and anim.time >= 0
      and anim.time < anim.duration // 2):
        image = MoveSprite(eyeball.facing)
        break
      elif type(anim) in (FlinchAnim, FlickerAnim):
        image = FlinchSprite(eyeball.facing)
        break
      elif type(anim) is BounceAnim:
        image = MoveSprite(eyeball.facing)
        offset_layer = "vfx"
        break
      elif type(anim) is Eyeball.ChargeAnim:
        image = ChargeSprite(eyeball.facing)
        offset_x = anim.offset
        break
    else:
      if eyeball.ailment == "sleep":
        image = SleepSprite(eyeball.facing)
      elif eyeball.get_hp() < eyeball.get_hp_max() / 2:
        image = MoveSprite(eyeball.facing)
      else:
        image = IdleSprite(eyeball.facing)
    if eyeball.ailment == "freeze":
      image = FlinchSprite(eyeball.facing)
    sprite = image and Sprite(
      image=image,
      pos=(offset_x, offset_y),
      offset=offset_depth
    ) or None
    if offset_layer:
      sprite.layer = offset_layer
    return super().view(sprite and [sprite] or None, anims)
