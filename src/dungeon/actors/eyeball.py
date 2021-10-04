from random import randint, choice
import lib.vector as vector
from lib.cell import is_adjacent, neighborhood, manhattan

from dungeon.actors import DungeonActor
from dungeon.stage import Tile
from cores import Core, Stats
from assets import sprites
from skills import Skill
from skills.weapon.tackle import Tackle
from skills.armor.hpup import HpUp
from items.materials.angeltears import AngelTears

from anims.move import MoveAnim
from anims.attack import AttackAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from anims.bounce import BounceAnim
from anims.awaken import AwakenAnim
from anims.shake import ShakeAnim
from anims.pause import PauseAnim
from vfx.alertbubble import AlertBubble
from lib.sprite import Sprite
from lib.filters import replace_color
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
      return user.cell

  def __init__(eyeball, name="Eyeball", faction="enemy", facing=(0, 1), rare=False, clones=0, cloned=False, *args, **kwargs):
    super().__init__(Core(
      name=name,
      faction=faction,
      facing=facing,
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
    eyeball.ai_mode = DungeonActor.AI_LOOK
    eyeball.ai_target = eyeball.find_look_turns()
    eyeball.ai_path = None
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
    valid_cells = game.floor.find_walkable_room_cells(cell=eyeball.cell)
    return choice(valid_cells) if valid_cells else None

  def step_look(eyeball, game):
    if not eyeball.ai_target:
      eyeball.ai_mode = DungeonActor.AI_MOVE
      eyeball.ai_target = eyeball.find_move_target(game)
      eyeball.ai_path = eyeball.ai_target and game.floor.pathfind(
        start=eyeball.cell,
        goal=eyeball.ai_target,
        whitelist=game.floor.find_walkable_room_cells(cell=eyeball.cell)
      )
      return None
    find_adjacent_facings = lambda facing: (
      [(0, -1), (0, 1)]
        if facing[0]
        else [(-1, 0), (1, 0)]
    )
    eyeball.facing = choice(find_adjacent_facings(eyeball.facing))
    if type(eyeball.ai_target) is int:
      eyeball.ai_target -= 1
    eyeball.turns = 0
    return None

  def step_move(eyeball, game):
    if not eyeball.ai_target or eyeball.cell == eyeball.ai_target:
      eyeball.ai_mode = DungeonActor.AI_LOOK
      eyeball.ai_target = eyeball.find_look_turns()
      return None
    return ("move_to", eyeball.ai_target)

  def step_wander(eyeball, game):
    if eyeball.ai_mode == DungeonActor.AI_LOOK:
      command = eyeball.step_look(game)
    elif eyeball.ai_mode == DungeonActor.AI_MOVE:
      command = eyeball.step_move(game)
    cell = eyeball.cell
    elem = None
    while (not Tile.is_opaque(game.floor.get_tile_at(cell))
    and elem is None
    and manhattan(cell, eyeball.cell) <= Eyeball.VISION_RANGE
    ):
      cell = vector.add(cell, eyeball.facing)
      elem = next((e for e in game.floor.get_elems_at(cell) if isinstance(e, DungeonActor) and not eyeball.allied(e)), None)
    if elem:
      eyeball.alert(cell)
      return None
    return command

  def step(eyeball, game):
    if not eyeball.can_step():
      return None

    if eyeball.ai_mode == DungeonActor.AI_LOOK or not eyeball.aggro or not eyeball.ai_target:
      return eyeball.step_wander(game)

    if (eyeball.core.hp < eyeball.core.stats.hp
    and eyeball.clones < Eyeball.CLONES_MAX
    and (not eyeball.cloned or Eyeball.CLONES_CAN_CLONE)
    and randint(1, 3) == 1):
      return eyeball.charge(Eyeball.Meyetosis)
    elif eyeball.ai_mode == DungeonActor.AI_MOVE and is_adjacent(eyeball.cell, eyeball.ai_target) and (
    enemy := next((e for e in game.floor.get_elems_at(eyeball.ai_target) if (
      isinstance(e, DungeonActor)
      and not eyeball.allied(e)
    )), None)):
      return ("attack", enemy)
    elif eyeball.ai_mode == DungeonActor.AI_MOVE:
      return ("move_to", eyeball.ai_target)

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
