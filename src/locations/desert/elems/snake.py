from random import random, choice

from lib.cell import is_adjacent
from lib.sprite import Sprite
from colors.palette import RED
import assets

from dungeon.actors import DungeonActor
from cores import Core, Stats
from skills.weapon.tackle import Tackle

from anims.step import StepAnim
from anims.attack import AttackAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from anims.frame import FrameAnim


class Spritesheet:

  _create_empty_sprite_map = lambda: {
    (0, -1): None,
    (0, 1): None,
    (-1, 0): None,
    (1, 0): None,
  }

  @staticmethod
  def _normalize_facing(facing):
    if facing[0] and facing[1]:
      facing = (facing[0], 0)

    return facing

  idle_sprites = _create_empty_sprite_map()
  @classmethod
  def get_idle_sprite(cls, facing):
    return cls.idle_sprites[cls._normalize_facing(facing)]

  move_sprites = _create_empty_sprite_map()
  @classmethod
  def get_move_sprite(cls, facing):
    return cls.move_sprites[cls._normalize_facing(facing)]

  attack_sprites = _create_empty_sprite_map()
  @classmethod
  def get_attack_sprite(cls, facing):
    return cls.attack_sprites[cls._normalize_facing(facing)]

  charge_sprite = None
  @classmethod
  def get_charge_sprites(cls):
    return cls._charge_sprites

  flinch_sprite = None
  @classmethod
  def get_flinch_sprite(cls):
    return cls._flinch_sprite


class DesertSnakeSpritesheet(Spritesheet):

  idle_sprites = {
    (0, -1): assets.sprites["snake_up"],
    (0, 1): assets.sprites["snake_down"],
    (-1, 0): assets.sprites["snake_side"],
    (1, 0): assets.sprites["snake_side"],
  }

  move_sprites = {
    (0, -1): assets.sprites["snake_move_up"],
    (0, 1): assets.sprites["snake_move_down"],
    (-1, 0): assets.sprites["snake_move_side"],
    (1, 0): assets.sprites["snake_move_side"],
  }

  attack_sprites = {
    (0, -1): (assets.sprites["snake_bite_open_up"], assets.sprites["snake_bite_closed_side"]),
    (0, 1): (assets.sprites["snake_bite_open_down"], assets.sprites["snake_bite_closed_side"]),
    (-1, 0): (assets.sprites["snake_bite_open_side"], assets.sprites["snake_bite_closed_side"]),
    (1, 0): (assets.sprites["snake_bite_open_side"], assets.sprites["snake_bite_closed_side"]),
  }

  _charge_sprites = assets.sprites["snake_charge"]
  _flinch_sprite = assets.sprites["snake_flinch"]


class DesertSnake(DungeonActor):

  def __init__(snake, name="King Tuto", *args, **kwargs):
    super().__init__(Core(
      name=name,
      faction="enemy",
      stats=Stats(
        hp=32,
        st=13,
        dx=8,
        ag=9,
        en=3,
      ),
      skills=[Tackle],
    ), *args, **kwargs)

  def get_message(snake):
    return choice([
      ("The ", snake.token(), " lies in wait."),
      ("The ", snake.token(), " lets out a mystic hiss."),
      ("The ", snake.token(), " sniffs a patch of dirt."),
    ])

  def find_move_delta(snake, target):
    snake_x, snake_y = snake.cell
    target_x, target_y = target.cell

    if snake_x < target_x:
      delta_x = 1
    elif snake_x > target_x:
      delta_x = -1
    else:
      delta_x = choice([-1, 1])

    if snake_y < target_y:
      delta_y = 1
    elif snake_y > target_y:
      delta_y = -1
    else:
      delta_y = choice([-1, 1])

    return (delta_x, delta_y)

  def step(snake, game):
    enemy = game.find_closest_enemy(snake)
    if not snake.aggro:
      return super().step(game)

    if not enemy:
      return None

    if random() < 1 / 16:
      game.anims.append([FrameAnim(
        target=snake,
        frames=DesertSnakeSpritesheet.get_charge_sprites() * 5,
        frames_duration=5,
      )])
      game.print(snake.get_message())
      return None

    if is_adjacent(snake.cell, enemy.cell):
      return ("attack", enemy)

    delta = snake.find_move_delta(target=enemy)
    return ("move", delta)

  def view(snake, anims):
    snake_image = DesertSnakeSpritesheet.get_idle_sprite(snake.facing)

    anim_group = [a for a in anims[0] if a.target is snake] if anims else []
    for anim in anim_group:
      if isinstance(anim, StepAnim):
        snake_image = DesertSnakeSpritesheet.get_move_sprite(snake.facing)
        break

      if isinstance(anim, AttackAnim):
        attack_sprites = DesertSnakeSpritesheet.get_attack_sprite(snake.facing)
        if (anim.time >= 0
        and anim.time < anim.duration // 2):
          snake_image = attack_sprites[0]
        elif anim.time >= anim.duration // 2:
          snake_image = attack_sprites[1]
        break

      if isinstance(anim, (FlinchAnim, FlickerAnim)):
        snake_image = DesertSnakeSpritesheet.get_flinch_sprite()
        break

    return super().view([Sprite(
      image=snake_image
    )], anims)
