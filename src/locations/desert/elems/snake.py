from lib.sprite import Sprite
import assets

from dungeon.actors import DungeonActor
from cores import Core, Stats
from skills.weapon.tackle import Tackle

from anims.step import StepAnim
from anims.attack import AttackAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim


class Spritesheet:

  _create_empty_sprite_map = lambda: {
    (0, -1): None,
    (0, 1): None,
    (-1, 0): None,
    (1, 0): None,
  }

  _idle_sprites = _create_empty_sprite_map()
  @classmethod
  def get_idle_sprite(cls, facing):
    return cls._idle_sprites[facing]

  _move_sprites = _create_empty_sprite_map()
  @classmethod
  def get_move_sprite(cls, facing):
    return cls._move_sprites[facing]

  _attack_sprites = _create_empty_sprite_map()
  @classmethod
  def get_attack_sprite(cls, facing):
    return cls._attack_sprites[facing]

  _flinch_sprites = _create_empty_sprite_map()
  @classmethod
  def get_flinch_sprite(cls):
    return cls._flinch_sprite


class DesertSnakeSpritesheet(Spritesheet):

  _idle_sprites = {
    (0, -1): assets.sprites["snake_up"],
    (0, 1): assets.sprites["snake_down"],
    (-1, 0): assets.sprites["snake_side"],
    (1, 0): assets.sprites["snake_side"],
  }

  _move_sprites = {
    (0, -1): assets.sprites["snake_move_up"],
    (0, 1): assets.sprites["snake_move_down"],
    (-1, 0): assets.sprites["snake_move_side"],
    (1, 0): assets.sprites["snake_move_side"],
  }

  _attack_sprites = {
    (0, -1): (assets.sprites["snake_bite_open_up"], assets.sprites["snake_bite_closed_side"]),
    (0, 1): (assets.sprites["snake_bite_open_down"], assets.sprites["snake_bite_closed_side"]),
    (-1, 0): (assets.sprites["snake_bite_open_side"], assets.sprites["snake_bite_closed_side"]),
    (1, 0): (assets.sprites["snake_bite_open_side"], assets.sprites["snake_bite_closed_side"]),
  }

  _flinch_sprite = assets.sprites["snake_flinch"]


class DesertSnake(DungeonActor):

  def __init__(snake, name="KingTuto", *args, **kwargs):
    super().__init__(Core(
      name=name,
      faction="enemy",
      stats=Stats(
        hp=32,
        st=13,
        dx=8,
        ag=7,
        en=3,
      ),
      skills=[Tackle],
    ), *args, **kwargs)

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
