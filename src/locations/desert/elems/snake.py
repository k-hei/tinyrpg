from random import random, choice

from lib.cell import is_adjacent
from lib.sprite import Sprite
from colors.palette import RED
import assets

from helpers.actor import Spritesheet
from dungeon.actors import DungeonActor
from cores import Core, Stats
from skills.weapon.tackle import Tackle

from anims.step import StepAnim
from anims.attack import AttackAnim
from anims.flinch import FlinchAnim
from anims.flicker import FlickerAnim
from anims.frame import FrameAnim


class DesertSnake(DungeonActor):
  spritesheet = Spritesheet(
    idle={
      (0, -1): assets.sprites["snake_up"],
      (0, 1): assets.sprites["snake_down"],
      (-1, 0): assets.sprites["snake_side"],
      (1, 0): assets.sprites["snake_side"],
    },
    move={
      (0, -1): assets.sprites["snake_move_up"],
      (0, 1): assets.sprites["snake_move_down"],
      (-1, 0): assets.sprites["snake_move_side"],
      (1, 0): assets.sprites["snake_move_side"],
    },
    attack={
      (0, -1): (assets.sprites["snake_bite_open_up"], assets.sprites["snake_bite_closed_side"]),
      (0, 1): (assets.sprites["snake_bite_open_down"], assets.sprites["snake_bite_closed_side"]),
      (-1, 0): (assets.sprites["snake_bite_open_side"], assets.sprites["snake_bite_closed_side"]),
      (1, 0): (assets.sprites["snake_bite_open_side"], assets.sprites["snake_bite_closed_side"]),
    },
    charge=assets.sprites["snake_charge"],
    flinch=assets.sprites["snake_flinch"],
  )

  idle_messages = [
    "The {enemy} lies in wait.",
    "The {enemy} lets out a mystic hiss.",
    "The {enemy} sniffs a patch of dirt.",
  ]

  def __init__(snake, name="King Tuto", *args, **kwargs):
    super().__init__(Core(
      name=name,
      faction="enemy",
      stats=Stats(
        hp=18,
        st=12,
        dx=8,
        ag=6,
        en=7,
      ),
      skills=[Tackle],
    ), *args, **kwargs)

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
    if not snake.can_step():
      return None

    if not snake.aggro:
      return super().step(game)

    enemy = game.find_closest_enemy(snake)
    if not enemy:
      return None

    if random() < 1 / 16 and snake.idle(game):
      game.anims[-1].append(FrameAnim(
        target=snake,
        frames=snake.spritesheet.get_charge_sprites() * 5,
        frames_duration=5,
      ))
      return None

    if is_adjacent(snake.cell, enemy.cell):
      return ("attack", enemy)

    delta = snake.find_move_delta(target=enemy)
    return ("move", delta)

  def find_image(snake, anims):
    if snake.ailment == "freeze":
      return snake.spritesheet.get_flinch_sprite()

    anim_group = [a for a in anims[0] if a.target is snake] if anims else []
    for anim in anim_group:
      if isinstance(anim, StepAnim):
        return snake.spritesheet.get_move_sprite(snake.facing)

      if isinstance(anim, AttackAnim):
        attack_sprites = snake.spritesheet.get_attack_sprite(snake.facing)
        if (anim.time >= 0
        and anim.time < anim.duration // 2):
          return attack_sprites[0]
        elif anim.time >= anim.duration // 2:
          return attack_sprites[1]
        break

      if isinstance(anim, (FlinchAnim, FlickerAnim)):
        return snake.spritesheet.get_flinch_sprite()

    return snake.spritesheet.get_idle_sprite(snake.facing)

  def view(snake, anims):
    return super().view([Sprite(image=snake.find_image(anims))], anims)
